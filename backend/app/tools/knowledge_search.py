"""
tools/knowledge_search.py
--------------------------
Tool 1: search_company_documents

Yeh tool tab call hota hai jab user company ki policies, benefits,
WFH guidelines ya leave rules ke baare me sawal puchta hai.

FLOW (Hinglish me):
  1. Agent se natural language query milti hai (jaise "work from home policy")
  2. Gemini embedding model se query ka vector banta hai
  3. ChromaDB vector database me similarity search hoti hai
  4. 0.30 threshold se neeche wale irrelevant chunks filter out ho jaate hain
  5. Chunks ko JSON format me pack karke LLM ko diya jaata hai
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
    Search company policy documents for information about policies,
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
    logger.info("Tool execute ho raha hai: search_company_documents | Query: '%s'", query)

    try:
        # ChromaDB se query ke relevant chunks mangwate hain (threshold filtered)
        chunks = retrieve_relevant_chunks(query=query, k=settings.RETRIEVAL_TOP_K)

        # Agar koi bhi chunk threshold pass nahi kar paya
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
            logger.info("Query ke liye koi relevant chunk nahi mila: '%s'", query)
            return json.dumps(result)

        # Agent ke padhne ke liye clean JSON format banate hain
        results = []
        for chunk in chunks:
            results.append({
                "content": chunk.page_content.strip(),
                "source": chunk.metadata.get("source", "unknown"),
                "page": chunk.metadata.get("page"),
                "document_type": chunk.metadata.get("document_type"),
            })

        # Sources nikalte hain (citations frontend par dikhane ke liye)
        sources = extract_unique_sources(chunks)

        result = {
            "found": True,
            "results": results,
            "sources": sources,
            "retrieval_count": len(chunks),
        }

        logger.info(
            "search_company_documents ne %d chunks return kiye sources se: %s",
            len(chunks),
            [s["source"] for s in sources],
        )
        return json.dumps(result)

    except Exception as e:
        logger.error("search_company_documents me exception aaya: %s", e, exc_info=True)
        return json.dumps({
            "found": False,
            "error": "Failed to search company documents. Please try again.",
            "results": [],
            "sources": [],
        })
