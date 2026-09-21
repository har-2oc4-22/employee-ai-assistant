"""
tests/test_agent.py
-------------------
Unit tests for conversation state memory and agent system prompt invariants.
"""

import pytest
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.state import get_history, save_history, clear_history
from app.prompts.agent_prompts import AGENT_SYSTEM_PROMPT


class TestConversationMemory:
    """Test conversation state and history window."""

    def test_save_and_retrieve_history(self):
        conv_id = "test-conv-state-1"
        msgs = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi, how can I help?"),
        ]
        save_history(conv_id, msgs)
        history = get_history(conv_id)
        assert len(history) == 2
        assert history[0].content == "Hello"
        assert history[1].content == "Hi, how can I help?"
        clear_history(conv_id)

    def test_history_window_trimming(self):
        from app.config import settings
        conv_id = "test-conv-window"
        # Generate 25 messages
        msgs = [HumanMessage(content=f"Message {i}") for i in range(25)]
        save_history(conv_id, msgs)
        history = get_history(conv_id)
        # Should be trimmed to MAX_CONVERSATION_HISTORY
        assert len(history) == settings.MAX_CONVERSATION_HISTORY
        assert history[-1].content == "Message 24"
        clear_history(conv_id)

    def test_clear_history(self):
        conv_id = "test-conv-clear"
        save_history(conv_id, [HumanMessage(content="Test")])
        assert len(get_history(conv_id)) == 1
        clear_history(conv_id)
        assert len(get_history(conv_id)) == 0


class TestPromptSafetyInvariants:
    """Ensure critical security and anti-hallucination guidelines are in system prompts."""

    def test_system_prompt_contains_anti_hallucination_rule(self):
        assert "never invent" in AGENT_SYSTEM_PROMPT.lower() or "not find" in AGENT_SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_prompt_injection_defense(self):
        assert "untrusted" in AGENT_SYSTEM_PROMPT.lower()
        assert "ignore" in AGENT_SYSTEM_PROMPT.lower()

    def test_system_prompt_restricts_leave_modification_to_tool(self):
        assert "apply_leave" in AGENT_SYSTEM_PROMPT
