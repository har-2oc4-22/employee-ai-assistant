"""
rag/vector_store.py
--------------------
Clean abstraction for ChromaDB operations.

WHY A SEPARATE ABSTRACTION?
  If we ever want to swap ChromaDB for another vector store (Pinecone, Weaviate, etc.)
  we only change this file — everything else uses the same VectorStore interface.
"""

import logging
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Returns the Google Gemini embeddings model.
    
    WHY Gemini embeddings?
    - models/gemini-embedding-001: Google's latest high-quality embedding model
    - 3072-dimensional vectors, optimised for semantic similarity search
    - Free-tier friendly — much cheaper than OpenAI equivalents
    """
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Returns a persistent ChromaDB client.
    
    WHY persistent?  So embeddings survive backend restarts.
    In-memory ChromaDB would require re-embedding on every restart.
    """
    return chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIRECTORY,
    )


def get_vector_store() -> Chroma:
    """
    Returns a LangChain Chroma vector store connected to our persistent client.
    This is the main object used for adding documents and running similarity search.
    """
    embeddings = get_embeddings()
    client = get_chroma_client()

    vector_store = Chroma(
        client=client,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
    logger.info(
        "Connected to ChromaDB collection '%s' at '%s'",
        settings.CHROMA_COLLECTION_NAME,
        settings.CHROMA_PERSIST_DIRECTORY,
    )
    return vector_store


def add_documents_to_store(documents: List[Document]) -> None:
    """
    Add a list of LangChain Document objects (with metadata) to ChromaDB.
    Called by the ingestion pipeline.
    """
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    logger.info("Added %d document chunks to ChromaDB.", len(documents))


def similarity_search_with_scores(
    query: str,
    k: int = 4,
) -> List[tuple[Document, float]]:
    """
    Run a similarity search and return (document, relevance_score) tuples.

    ChromaDB natively returns L2 distance (lower = more similar, range 0–∞).
    LangChain's `similarity_search_with_relevance_scores` converts this to a
    0-to-1 relevance score (higher = more similar) using an exponential decay function.

    WHY convert?  The threshold in config (RETRIEVAL_SCORE_THRESHOLD=0.70) is expressed
    as a relevance fraction, which is more intuitive than raw L2 distance.
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(query=query, k=k)
    return results


def get_collection_count() -> int:
    """Return the number of chunks currently stored in ChromaDB."""
    client = get_chroma_client()
    try:
        col = client.get_collection(settings.CHROMA_COLLECTION_NAME)
        return col.count()
    except Exception:
        return 0


def clear_collection() -> None:
    """Delete and recreate the collection (used for force re-ingestion)."""
    client = get_chroma_client()
    try:
        client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        logger.info("Cleared ChromaDB collection '%s'.", settings.CHROMA_COLLECTION_NAME)
    except Exception as e:
        logger.warning("Could not delete collection: %s", e)
