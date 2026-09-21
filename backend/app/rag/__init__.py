"""
rag/__init__.py
"""
from .ingestion import ingest_documents
from .retriever import retrieve_relevant_chunks, format_retrieved_context, extract_unique_sources
from .vector_store import get_vector_store, get_collection_count

__all__ = [
    "ingest_documents",
    "retrieve_relevant_chunks",
    "format_retrieved_context",
    "extract_unique_sources",
    "get_vector_store",
    "get_collection_count",
]
