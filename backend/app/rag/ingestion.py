"""
rag/ingestion.py
-----------------
Document ingestion pipeline (RAG data preparation).

DATA PIPELINE FLOW (Hinglish me samjhein):
  Documents (PDF / Markdown / Text)
    → Document Loader       (Files ko padhkar text nikalna)
    → Text Splitting        (800 characters ke chunks banana with 150 overlap)
    → Gemini Embeddings     (Har chunk ka vector number representation banana)
    → ChromaDB              (Persistent disk storage me save karna)

Yeh module do jagah use hota hai:
  1. scripts/ingest_documents.py (Terminal CLI se run karne par)
  2. api/routes/ingestion.py     (POST /ingest API endpoint par)
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
    Ek single document file ko padhta hai aur uski metadata enrich karta hai.

    ALAG ALAG LOADERS KYU?
    - PDF files me multiple pages hote hain, isliye PyPDFLoader page number track karta hai.
    - Markdown aur TXT files plain text hoti hain, jinhe TextLoader clean format me read karta hai.
    """
    ext = Path(file_path).suffix.lower()
    filename = Path(file_path).name

    try:
        if ext == ".pdf":
            # PDF file load karke page-by-page metadata add karte hain
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            for i, doc in enumerate(docs):
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "pdf"
                doc.metadata["page"] = doc.metadata.get("page", i) + 1

        elif ext == ".md":
            # Markdown file load kar rahe hain
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "md"
                doc.metadata.setdefault("page", 1)

        elif ext == ".txt":
            # Normal text file load kar rahe hain
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = filename
                doc.metadata["document_type"] = "txt"
                doc.metadata.setdefault("page", 1)

        else:
            logger.warning("Unsupported file type '%s', isko skip kar rahe hain.", ext)
            return []

        logger.info("File load hui '%s' -> %d page(s)", filename, len(docs))
        return docs

    except Exception as e:
        logger.error("File '%s' load karne me error aaya: %s", file_path, e)
        return []


def load_all_documents(documents_dir: str) -> List[Document]:
    """
    Documents folder ke andar jitne bhi supported files hain (.pdf, .txt, .md),
    un sabko ek sath load karke ek flat list return karta hai.
    """
    supported_extensions = {".pdf", ".txt", ".md"}
    all_docs: List[Document] = []

    if not os.path.exists(documents_dir):
        raise FileNotFoundError(f"Documents directory nahi mila: {documents_dir}")

    files = list(Path(documents_dir).glob("*"))
    files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]

    if not files:
        logger.warning("Folder '%s' me koi supported document nahi mila.", documents_dir)
        return []

    for file_path in files:
        docs = load_single_document(str(file_path))
        all_docs.extend(docs)

    logger.info("Total %d files me se %d pages load hue.", len(files), len(all_docs))
    return all_docs


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Documents ko chote chunks me divide karta hai taaki LLM context window me fit ho sakein.

    RECURSIVE CHARACTER TEXT SPLITTER KYU?
    - Yeh pehle paragraph (\n\n), fir sentence (\n, .), fir words ke basis par split karta hai.
    - Isse text ka context aur meaning barkarar rehta hai.
    
    CHUNK SIZE = 800, CHUNK OVERLAP = 150 KYU?
    - 800 characters (~160 tokens) me policy ka pura clause ache se cover ho jata hai.
    - 150 characters overlap isliye rakhte hain taaki do chunks ke border par sentences cut na ho jayein.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        # Split karne ka priority order
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    logger.info(
        "%d pages ko %d chunks me split kiya (size=%d, overlap=%d).",
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
    Complete ingestion pipeline execute karne ka main function:
    1. Disk se documents load karo
    2. Chunks me split karo
    3. Gemini embeddings banakar ChromaDB me persist karo
    """
    from app.rag.vector_store import clear_collection

    documents_dir = documents_dir or settings.DOCUMENTS_DIR

    # Agar user ne force_reingest bola hai toh purana ChromaDB data delete karo
    if force_reingest:
        logger.info("Force re-ingest manga gaya hai — purana collection delete kar rahe hain.")
        clear_collection()

    # Agar pehle se data maujood hai aur force_reingest false hai toh skip karo
    existing_count = get_collection_count()
    if existing_count > 0 and not force_reingest:
        logger.info(
            "ChromaDB me pehle se %d chunks hain. Ingestion skip kar rahe hain.",
            existing_count,
        )
        return {
            "status": "skipped",
            "reason": "Documents already ingested",
            "existing_chunks": existing_count,
        }

    # Step 1: Documents Load karo
    logger.info("Documents load ho rahe hain from: %s", documents_dir)
    raw_docs = load_all_documents(documents_dir)
    if not raw_docs:
        return {"status": "error", "reason": "No documents found"}

    # Step 2: Chunks banao
    chunks = split_documents(raw_docs)

    # Step 3: Embeddings generate karke ChromaDB me store karo
    logger.info("%d chunks ko ChromaDB me store kar rahe hain...", len(chunks))
    add_documents_to_store(chunks)

    final_count = get_collection_count()
    logger.info("Ingestion complete ho gaya! DB me total chunks: %d", final_count)

    return {
        "status": "success",
        "documents_loaded": len(set(d.metadata.get("source", "") for d in raw_docs)),
        "chunks_created": len(chunks),
        "total_chunks_in_db": final_count,
    }
