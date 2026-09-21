"""
models/chat.py
--------------
Pydantic models for all chat-related request/response bodies.
Using Pydantic ensures automatic validation and clear API documentation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Incoming chat request from the React frontend.
    employee_id:      who is asking (e.g. "EMP001")
    message:          the user's natural language question
    conversation_id:  optional; if omitted the backend creates a new one
    """
    employee_id: str = Field(..., description="Employee ID, e.g. EMP001")
    message: str = Field(..., min_length=1, description="User's question or command")
    conversation_id: Optional[str] = Field(
        None, description="Pass back the ID from the previous response to continue a conversation"
    )


# ── Source document cited in a RAG response ───────────────────────────────

class SourceDocument(BaseModel):
    """A single source chunk retrieved from ChromaDB."""
    source: str = Field(..., description="Document filename, e.g. leave_policy.pdf")
    page: Optional[int] = Field(None, description="Page number inside the document")
    document_type: Optional[str] = Field(None, description="pdf / md / txt")


# ── Response ──────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    """
    Outgoing chat response sent back to the React frontend.
    Every field has a default so the backend never crashes with a missing key.
    """
    conversation_id: str = Field(..., description="Use this in the next request to continue the conversation")
    answer: str = Field(..., description="The assistant's answer")
    sources: List[SourceDocument] = Field(
        default_factory=list,
        description="Source documents used (only populated for RAG answers)"
    )
    tools_used: List[str] = Field(
        default_factory=list,
        description="Names of the tools the agent invoked to answer this question"
    )


# ── Ingestion trigger ─────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Body for the POST /ingest endpoint."""
    secret: str = Field(..., description="Must match INGEST_SECRET in .env")
    force_reingest: bool = Field(
        False,
        description="If True, re-embed all documents even if already stored"
    )
