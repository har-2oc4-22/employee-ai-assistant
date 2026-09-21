"""
tests/test_rag.py
------------------
Tests for the RAG retrieval pipeline (retriever and ingestion logic).

These tests mock ChromaDB to avoid requiring an actual ChromaDB instance.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("GEMINI_API_KEY", "test-key")


class TestRetriever:
    """Tests for retrieve_relevant_chunks and helper functions."""

    @patch("app.rag.retriever.similarity_search_with_scores")
    def test_returns_chunks_above_threshold(self, mock_search):
        """Chunks with high relevance scores should be returned."""
        from langchain_core.documents import Document
        from app.rag.retriever import retrieve_relevant_chunks

        mock_doc = Document(
            page_content="Employees can work from home up to 2 days a week.",
            metadata={"source": "work_from_home_policy.md", "page": 1},
        )
        mock_search.return_value = [(mock_doc, 0.85)]  # Above threshold

        # Temporarily lower threshold for test
        with patch("app.rag.retriever.settings") as mock_settings:
            mock_settings.RETRIEVAL_TOP_K = 4
            mock_settings.RETRIEVAL_SCORE_THRESHOLD = 0.70
            results = retrieve_relevant_chunks("work from home policy")

        assert len(results) == 1
        assert "work from home" in results[0].page_content

    @patch("app.rag.retriever.similarity_search_with_scores")
    def test_filters_chunks_below_threshold(self, mock_search):
        """Chunks below the threshold should be filtered out (hallucination guard)."""
        from langchain_core.documents import Document
        from app.rag.retriever import retrieve_relevant_chunks

        mock_doc = Document(
            page_content="Some weakly related content.",
            metadata={"source": "some_doc.md", "page": 1},
        )
        mock_search.return_value = [(mock_doc, 0.20)]  # Below threshold

        with patch("app.rag.retriever.settings") as mock_settings:
            mock_settings.RETRIEVAL_TOP_K = 4
            mock_settings.RETRIEVAL_SCORE_THRESHOLD = 0.70
            results = retrieve_relevant_chunks("pet insurance")

        assert len(results) == 0  # Should be empty — hallucination prevented

    @patch("app.rag.retriever.similarity_search_with_scores")
    def test_empty_db_returns_empty(self, mock_search):
        """When ChromaDB has no results, return empty list."""
        from app.rag.retriever import retrieve_relevant_chunks

        mock_search.return_value = []
        results = retrieve_relevant_chunks("anything")
        assert results == []


class TestSourceExtraction:
    """Tests for extract_unique_sources."""

    def test_deduplicates_sources(self):
        from langchain_core.documents import Document
        from app.rag.retriever import extract_unique_sources

        chunks = [
            Document(page_content="...", metadata={"source": "leave_policy.md", "page": 1}),
            Document(page_content="...", metadata={"source": "leave_policy.md", "page": 1}),  # duplicate
            Document(page_content="...", metadata={"source": "leave_policy.md", "page": 2}),
        ]
        sources = extract_unique_sources(chunks)
        assert len(sources) == 2  # page 1 and page 2, no duplicates

    def test_source_has_expected_fields(self):
        from langchain_core.documents import Document
        from app.rag.retriever import extract_unique_sources

        chunks = [
            Document(
                page_content="...",
                metadata={"source": "it_policy.md", "page": 3, "document_type": "md"},
            )
        ]
        sources = extract_unique_sources(chunks)
        assert sources[0]["source"] == "it_policy.md"
        assert sources[0]["page"] == 3


class TestContextFormatting:
    """Tests for format_retrieved_context."""

    def test_formats_with_source_label(self):
        from langchain_core.documents import Document
        from app.rag.retriever import format_retrieved_context

        chunks = [
            Document(
                page_content="Employees get 18 days of EL.",
                metadata={"source": "leave_policy.md", "page": 2},
            )
        ]
        context = format_retrieved_context(chunks)
        assert "leave_policy.md" in context
        assert "Employees get 18 days of EL." in context

    def test_empty_chunks_returns_empty_string(self):
        from app.rag.retriever import format_retrieved_context
        assert format_retrieved_context([]) == ""
