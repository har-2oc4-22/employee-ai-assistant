"""
rag/retriever.py
-----------------
Retrieval logic: Given a query, find the most relevant document chunks.
Yeh module user ke sawal ke hisaab se sabse relevant policy documents dhoondta hai.

HALLUCINATION PREVENTION KAISE KAAM KARTA HAI (Hinglish me):
  1. ChromaDB cosine similarity search karta hai aur har chunk ko relevance score (0 se 1) deta hai.
  2. Agar koi bhi chunk RETRIEVAL_SCORE_THRESHOLD (0.30) se upar nahi score karta, toh empty list return hoti hai.
  3. Jab empty list aati hai, LLM ko pata chal jata hai ki company policy me yeh information maujood nahi hai.
  4. Isse LLM mann-ghadant (hallucinated) jawab nahi banata aur saaf bolta hai ki documents me answer nahi mila.
"""

import logging
from typing import List

from langchain_core.documents import Document

from app.config import settings
from app.rag.vector_store import similarity_search_with_scores

logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(query: str, k: int = None) -> List[Document]:
    """
    User query ke liye top-k most relevant document chunks retrieve karta hai.

    Kaise kaam karta hai:
    1. ChromaDB me similarity search chalata hai (query vector vs document vectors).
    2. Threshold filter lagata hai (kam score wale irrelevant chunks ko hata deta hai).
    3. Filtered documents return karta hai (with file name aur page metadata).
    """
    k = k or settings.RETRIEVAL_TOP_K
    threshold = settings.RETRIEVAL_SCORE_THRESHOLD

    # ChromaDB se similarity search karate hain (returns [(Document, score), ...])
    results_with_scores = similarity_search_with_scores(query=query, k=k)

    if not results_with_scores:
        logger.info("ChromaDB se query '%s' ke liye koi result nahi mila", query)
        return []

    # Har result ka similarity score log karte hain (debugging ke liye)
    for doc, score in results_with_scores:
        logger.debug(
            "  Score: %.3f | Source: %s",
            score,
            doc.metadata.get("source", "unknown"),
        )

    # Threshold filtering: Sirf wahi chunks rakho jinka score >= threshold hai
    filtered = [
        (doc, score)
        for doc, score in results_with_scores
        if score >= threshold
    ]

    # Agar sabhi chunks threshold se neeche hain, matlab documents me answer nahi hai
    if not filtered:
        logger.info(
            "Sare %d chunks threshold %.2f se neeche score kare query ke liye: '%s'",
            len(results_with_scores),
            threshold,
            query,
        )
        return []

    logger.info(
        "Threshold %.2f ke upar %d/%d chunks select hue query ke liye: '%s'",
        threshold,
        len(filtered),
        len(results_with_scores),
        query,
    )

    # Sirf document objects return karte hain
    return [doc for doc, _ in filtered]


def format_retrieved_context(chunks: List[Document]) -> str:
    """
    Retrieved document chunks ko ek single clean text string me convert karta hai
    taaki Gemini ke prompt me context ke roop me bheja ja sake.
    
    Har chunk ke upar source document ka naam aur page number likha rehta hai:
    [Source: leave_policy.md | Page: 2]
    ...content...
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
    Retrieved chunks me se unique source references nikalta hai (duplicates remove karke).
    Yeh frontend me '📄 Sources' pill tags display karne ke kaam aata hai.
    """
    seen = set()
    sources = []

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page")
        doc_type = chunk.metadata.get("document_type")

        # Duplicate sources avoid karne ke liye unique key banate hain
        key = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": source,
                "page": page,
                "document_type": doc_type,
            })

    return sources
