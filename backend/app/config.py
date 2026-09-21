"""
config.py
---------
Central configuration module.
All settings are loaded from environment variables (via .env file).
This keeps secrets out of source code and makes the app easy to configure.
"""

import os
from dotenv import load_dotenv

# Load the .env file from the backend directory
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    Every setting has a sensible default so the app can start for development.
    In production, always set these explicitly.
    """

    # ── Google Gemini ────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Chat model: gemini-3.6-flash is fast + capable
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")
    # Embedding model: models/gemini-embedding-001 is Google's best semantic search model
    GEMINI_EMBEDDING_MODEL: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001"
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    # Path where ChromaDB persists its data on disk
    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY", "./chroma_db"
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "employee_documents"
    )

    # ── Retrieval ─────────────────────────────────────────────────────────────
    # How many chunks to retrieve per query (top-k)
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))
    # ChromaDB returns L2 distance scores. Lower = more similar.
    # We convert to a 0-1 relevance score; this threshold is the MINIMUM
    # relevance we accept before refusing to answer (hallucination guard).
    RETRIEVAL_SCORE_THRESHOLD: float = float(
        os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.70")
    )

    # ── RAG chunking ──────────────────────────────────────────────────────────
    # chunk_size=800: large enough to keep a coherent policy paragraph together
    # chunk_overlap=150: ensures ideas at chunk boundaries aren't lost
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # ── Data paths ────────────────────────────────────────────────────────────
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", "./data/documents")
    EMPLOYEES_FILE: str = os.getenv("EMPLOYEES_FILE", "./data/employees.json")
    LEAVE_REQUESTS_FILE: str = os.getenv(
        "LEAVE_REQUESTS_FILE", "./data/leave_requests.json"
    )

    # ── API / CORS ────────────────────────────────────────────────────────────
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

    # ── Conversation memory ───────────────────────────────────────────────────
    # Maximum number of past messages kept in memory per conversation
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))

    # ── Ingestion protection ──────────────────────────────────────────────────
    INGEST_SECRET: str = os.getenv("INGEST_SECRET", "dev-ingest-secret")

    def validate(self) -> None:
        """Raise an error if critical settings are missing."""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Please add it to your backend/.env file."
            )


# Singleton instance used throughout the app
settings = Settings()
