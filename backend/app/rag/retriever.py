"""
rag/retriever.py
-----------------
Retrieval logic: given a query, find the most relevant document chunks.

HOW HALLUCINATION PREVENTION WORKS:
  After similarity search, each chunk has a relevance score (0–1).
  If NO chunk scores above RETRIEVAL_SCORE_THRESHOLD, we return an empty list.
  The calling code treats empty results as "not found" and tells the LLM so,
  preventing it from inventing an answer from its training data.
"""

import logging
from typing import List

from langchain_core.documents import Document

from app.config import settings
from app.rag.vector_store import similarity_search_with_scores

logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(query: str, k: int = None) -> List[Document]:
    """
    Retrieve the top-k most relevant document chunks for a query.

    Steps:
    1. Run similarity search in ChromaDB.
    2. Filter out chunks below the relevance threshold.
    3. Return the remaining chunks (with metadata intact).

    If no chunks pass the threshold → returns empty list.
    The caller should then NOT pass any context to the LLM
    (which prevents hallucination).
    """
    k = k or settings.RETRIEVAL_TOP_K
    threshold = settings.RETRIEVAL_SCORE_THRESHOLD

    # Run search (returns [(Document, relevance_score), ...])
    results_with_scores = similarity_search_with_scores(query=query, k=k)

    if not results_with_scores:
        logger.info("No results returned from ChromaDB for query: '%s'", query)
        return []

    # Log scores for transparency
    for doc, score in results_with_scores:
        logger.debug(
            "  Score: %.3f | Source: %s",
            score,
            doc.metadata.get("source", "unknown"),
        )

    # Filter by threshold
    filtered = [
        (doc, score)
        for doc, score in results_with_scores
        if score >= threshold
    ]

    if not filtered:
        logger.info(
            "All %d retrieved chunks scored below threshold %.2f for query: '%s'",
            len(results_with_scores),
            threshold,
            query,
        )
        return []

    logger.info(
        "Retrieved %d/%d chunks above threshold %.2f for query: '%s'",
        len(filtered),
        len(results_with_scores),
        threshold,
        query,
    )

    # Return just the documents (scores were only needed for filtering)
    return [doc for doc, _ in filtered]


def format_retrieved_context(chunks: List[Document]) -> str:
    """
    Format retrieved chunks into a single context string to inject into the prompt.
    Each chunk is labelled with its source so the LLM can cite it.

    Example output:
      [Source: leave_policy.md | Page: 2]
      Employees are entitled to 18 days of Earned Leave...

      [Source: leave_policy.md | Page: 3]
      Casual Leave cannot be carried forward...
    """
    if not chunks:
        return ""

    parts = []
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", "")
        page_label = f" | Page: {page}" if page else ""
        parts.append(f"[Source: {source}{page_label}]\n{chunk.page_content.strip()}")

    return "\n\n---\n\n".join(parts)


def extract_unique_sources(chunks: List[Document]) -> List[dict]:
    """
    Extract deduplicated source references from retrieved chunks.
    Used to populate the 'sources' field in the API response.

    Returns a list like:
      [{"source": "leave_policy.md", "page": 2, "document_type": "md"}, ...]
    """
    seen = set()
    sources = []

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page")
        doc_type = chunk.metadata.get("document_type")

        # Use (source, page) as the unique key to avoid duplicates
        key = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": source,
                "page": page,
                "document_type": doc_type,
            })

    return sources
