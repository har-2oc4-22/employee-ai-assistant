"""
tools/knowledge_search.py
--------------------------
Tool 1: search_company_documents

The agent calls this tool whenever the user asks about company policies,
procedures, benefits, or any other company-specific information.

HOW IT WORKS:
  1. Receive a natural language query from the agent.
  2. Embed the query using Gemini embeddings (same model used for documents).
  3. Search ChromaDB for the most similar chunks.
  4. Filter chunks below the relevance threshold (hallucination guard).
  5. Return the chunks as a JSON string (the agent reads this to answer).
"""

import json
import logging
from typing import Any

from langchain_core.tools import tool

from app.config import settings
from app.rag.retriever import extract_unique_sources, retrieve_relevant_chunks

logger = logging.getLogger(__name__)


@tool
def search_company_documents(query: str) -> str:
    """
    Search TechCorp's company documents for information about policies,
    benefits, procedures, or any other company-specific topic.
    
    Use this tool for ANY question about:
    - Leave policy, WFH policy, travel policy
    - Employee benefits, health insurance, wellness programmes
    - IT and security policies
    - Company FAQ, onboarding, exit procedures
    - Any company-specific rules or guidelines

    Args:
        query: A natural language search query (e.g. "work from home policy")

    Returns:
        JSON string with retrieved document chunks and source citations.
    """
    logger.info("Tool: search_company_documents | Query: '%s'", query)

    try:
        chunks = retrieve_relevant_chunks(query=query, k=settings.RETRIEVAL_TOP_K)

        if not chunks:
            result = {
                "found": False,
                "message": (
                    "No sufficiently relevant information was found in the company documents "
                    f"for the query: '{query}'. "
                    "Please tell the user you couldn't find this information."
                ),
                "results": [],
                "sources": [],
            }
            logger.info("No relevant chunks found for query: '%s'", query)
            return json.dumps(result)

        # Format results for the agent
        results = []
        for chunk in chunks:
            results.append({
                "content": chunk.page_content.strip(),
                "source": chunk.metadata.get("source", "unknown"),
                "page": chunk.metadata.get("page"),
                "document_type": chunk.metadata.get("document_type"),
            })

        sources = extract_unique_sources(chunks)

        result = {
            "found": True,
            "results": results,
            "sources": sources,
            "retrieval_count": len(chunks),
        }

        logger.info(
            "Tool: search_company_documents returned %d chunks from sources: %s",
            len(chunks),
            [s["source"] for s in sources],
        )
        return json.dumps(result)

    except Exception as e:
        logger.error("Error in search_company_documents: %s", e, exc_info=True)
        return json.dumps({
            "found": False,
            "error": "Failed to search company documents. Please try again.",
            "results": [],
            "sources": [],
        })
