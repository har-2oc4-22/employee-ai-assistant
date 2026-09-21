"""
services/chat_service.py
-------------------------
Chat service — bridges the API layer and the agent.

This service:
  1. Validates the request.
  2. Calls the agent.
  3. Converts the agent output to a ChatResponse Pydantic model.

WHY A SEPARATE SERVICE?
  It keeps the route handler thin (HTTP concerns only) and the agent
  focused on AI logic. If we wanted to add rate-limiting, logging,
  or caching, we add it here without touching routes or the agent.
"""

import logging
from typing import Optional

from app.agent.agent import run_agent
from app.models.chat import ChatResponse, SourceDocument

logger = logging.getLogger(__name__)


def process_chat(
    employee_id: str,
    message: str,
    conversation_id: Optional[str] = None,
) -> ChatResponse:
    """
    Process a single chat message and return a structured response.
    """
    logger.info(
        "Processing chat | emp=%s | conv=%s | msg='%s'",
        employee_id, conversation_id, message[:80],
    )

    # Run the agent (synchronous — runs in thread pool via FastAPI's run_in_threadpool)
    result = run_agent(
        employee_id=employee_id,
        user_message=message,
        conversation_id=conversation_id,
    )

    # Convert raw source dicts to SourceDocument Pydantic models
    sources = [
        SourceDocument(
            source=s.get("source", "unknown"),
            page=s.get("page"),
            document_type=s.get("document_type"),
        )
        for s in result.get("sources", [])
    ]

    return ChatResponse(
        conversation_id=result["conversation_id"],
        answer=result["answer"],
        sources=sources,
        tools_used=result.get("tools_used", []),
    )
