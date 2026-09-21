"""
agent/state.py
--------------
Conversation memory management.

HOW IT WORKS:
  We use a simple in-memory dictionary:
    conversation_id (str) → list of LangChain messages

  WHY IN-MEMORY (for this assessment)?
    Simple, fast, and requires no external dependencies.
    The interface is designed so you can replace it with Redis or a database
    without changing any other code.

  HISTORY WINDOW:
    We only keep the last MAX_CONVERSATION_HISTORY messages.
    This prevents the context window from overflowing on long conversations.
    (Gemini has token limits — unlimited history would overflow the context too.)
"""

import logging
from typing import Dict, List

from langchain_core.messages import BaseMessage

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory store: conversation_id → list of messages
# In production, replace this with:
#   - Redis (for multi-instance deployments)
#   - PostgreSQL (for permanent history)
_conversation_store: Dict[str, List[BaseMessage]] = {}


def get_history(conversation_id: str) -> List[BaseMessage]:
    """
    Retrieve the conversation history for a given conversation ID.
    Returns an empty list for new conversations.
    """
    return _conversation_store.get(conversation_id, [])


def save_history(conversation_id: str, messages: List[BaseMessage]) -> None:
    """
    Save (overwrite) the conversation history.
    
    Applies the history window: only the last MAX_CONVERSATION_HISTORY messages
    are kept. This prevents infinite growth.
    """
    max_msgs = settings.MAX_CONVERSATION_HISTORY
    # Keep only the tail of the history
    trimmed = messages[-max_msgs:]
    _conversation_store[conversation_id] = trimmed

    logger.debug(
        "Saved conversation '%s': %d messages (trimmed to %d)",
        conversation_id, len(messages), len(trimmed),
    )


def clear_history(conversation_id: str) -> None:
    """Delete a conversation's history (called on reset)."""
    if conversation_id in _conversation_store:
        del _conversation_store[conversation_id]
        logger.info("Cleared conversation history for '%s'.", conversation_id)


def list_conversations() -> List[str]:
    """Return all active conversation IDs (for debugging)."""
    return list(_conversation_store.keys())
