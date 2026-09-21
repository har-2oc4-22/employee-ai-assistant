"""
rag/ingestion.py
-----------------
Document ingestion pipeline.

Flow:
  Documents (pdf/md/txt)
    → Document Loader       (LangChain loaders)
    → Text Extraction
    → Chunking              (RecursiveCharacterTextSplitter)
    → Gemini Embeddings
    → ChromaDB              (persistent storage)

This module is used by:
  - scripts/ingest_documents.py  (CLI)
  - api/routes/ingestion.py      (POST /ingest endpoint)
"""

import logging
import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.vector_store import add_documents_to_store, get_collection_count

logger = logging.getLogger(__name__)


def load_single_document(file_path: str) -> List[Document]:
    """
    Load a single document using the appropriate LangChain loader.

    WHY different loaders?
    - PDF files have page structure — PyPDFLoader preserves page numbers.
    - Markdown files have headings — UnstructuredMarkdownLoader handles them.
    - Plain text files are loaded with TextLoader.
    
    Returns a list of Document objects (one per page for PDF, one for MD/TXT).
    """
    ext = Path(file_path).suffix.lower()
    filename = Path(file_path).name

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # Enrich metadata for every page
            for i, doc in enumerate(docs):
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "pdf"
                # page is already set by PyPDFLoader (0-indexed), convert to 1-indexed
                doc.metadata["page"] = doc.metadata.get("page", i) + 1

        elif ext == ".md":
            # Use TextLoader for markdown — simpler than UnstructuredMarkdownLoader
            # Our policy .md files are plain text with standard markdown formatting.
            # TextLoader reads the raw text which the splitter then chunks cleanly.
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "md"
                doc.metadata.setdefault("page", 1)

        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "txt"
                doc.metadata.setdefault("page", 1)

        else:
            logger.warning("Unsupported file type '%s', skipping.", ext)
            return []

        logger.info("Loaded '%s' -> %d page(s)", filename, len(docs))
        return docs

    except Exception as e:
        logger.error("Failed to load '%s': %s", file_path, e)
        return []


def load_all_documents(documents_dir: str) -> List[Document]:
    """
    Walk the documents directory and load every supported file.
    Returns a flat list of LangChain Document objects.
    """
    supported_extensions = {".pdf", ".txt", ".md"}
    all_docs: List[Document] = []

    if not os.path.exists(documents_dir):
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    files = list(Path(documents_dir).glob("*"))
    files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]

    if not files:
        logger.warning("No supported documents found in '%s'.", documents_dir)
        return []

    for file_path in files:
        docs = load_single_document(str(file_path))
        all_docs.extend(docs)

    logger.info("Loaded %d total pages from %d files.", len(all_docs), len(files))
    return all_docs


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks suitable for embedding.

    WHY RecursiveCharacterTextSplitter?
    - It tries to split at natural boundaries: paragraphs → sentences → words.
    - This preserves semantic meaning better than a simple character split.

    WHY chunk_size=800, chunk_overlap=150?
    - 800 chars ≈ 150–180 tokens: fits comfortably in the model's context
      while large enough to contain a complete policy paragraph.
    - 150 char overlap ensures that ideas at chunk boundaries are not lost
      (e.g., a sentence that starts near the end of one chunk continues into the next).
    - These are starting values. In production, experiment with different sizes
      and measure retrieval quality using a test set of questions.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        # Separators tried in order: paragraph → sentence → word → char
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    logger.info(
        "Split %d pages into %d chunks (size=%d, overlap=%d).",
        len(documents),
        len(chunks),
        settings.CHUNK_SIZE,
        settings.CHUNK_OVERLAP,
    )
    return chunks


def ingest_documents(
    documents_dir: str = None,
    force_reingest: bool = False,
) -> dict:
    """
    Main ingestion function.
    
    1. Load documents from disk.
    2. Split into chunks.
    3. Embed and store in ChromaDB.

    force_reingest=True clears the existing collection first.
    Returns a summary dict with stats.
    """
    from app.rag.vector_store import clear_collection

    documents_dir = documents_dir or settings.DOCUMENTS_DIR

    # Optionally clear existing data
    if force_reingest:
        logger.info("Force re-ingest requested — clearing existing collection.")
        clear_collection()

    # Check if already ingested (skip unless forced)
    existing_count = get_collection_count()
    if existing_count > 0 and not force_reingest:
        logger.info(
            "ChromaDB already contains %d chunks. Skipping ingestion. "
            "Pass force_reingest=True to re-embed.",
            existing_count,
        )
        return {
            "status": "skipped",
            "reason": "Documents already ingested",
            "existing_chunks": existing_count,
        }

    # Load
    logger.info("Loading documents from: %s", documents_dir)
    raw_docs = load_all_documents(documents_dir)
    if not raw_docs:
        return {"status": "error", "reason": "No documents found"}

    # Split
    chunks = split_documents(raw_docs)

    # Store
    logger.info("Storing %d chunks in ChromaDB...", len(chunks))
    add_documents_to_store(chunks)

    final_count = get_collection_count()
    logger.info("Ingestion complete. Total chunks in DB: %d", final_count)

    return {
        "status": "success",
        "documents_loaded": len(set(d.metadata.get("source", "") for d in raw_docs)),
        "chunks_created": len(chunks),
        "total_chunks_in_db": final_count,
    }
