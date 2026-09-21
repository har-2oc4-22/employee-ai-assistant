"""
tests/test_chat.py
-------------------
Integration tests for the FastAPI /chat and /health endpoints.

These tests use TestClient (httpx-based) and mock the agent
to avoid requiring a real Gemini key during CI.
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["EMPLOYEES_FILE"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "employees.json"
)


# Mock the agent before importing the app
MOCK_AGENT_RESPONSE = {
    "answer": "You have 12 days of leave remaining.",
    "sources": [],
    "tools_used": ["get_employee_info"],
    "conversation_id": "test-conv-123",
}


from app.main import app

# Use raise_server_exceptions=False to ignore lifespan errors in tests
client = TestClient(app, raise_server_exceptions=False)


class TestHealth:
    """Test the health check endpoint."""

    def test_health_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestChatEndpoint:
    """Test the /chat endpoint."""

    @patch("app.api.routes.chat.process_chat")
    def test_chat_valid_request(self, mock_process):
        from app.models.chat import ChatResponse
        mock_process.return_value = ChatResponse(
            conversation_id="test-conv-123",
            answer="You have 12 days of leave remaining.",
            sources=[],
            tools_used=["get_employee_info"],
        )

        response = client.post(
            "/chat",
            json={
                "employee_id": "EMP001",
                "message": "How many leaves do I have?",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "conversation_id" in data
        assert "sources" in data
        assert "tools_used" in data

    def test_chat_invalid_employee(self):
        response = client.post(
            "/chat",
            json={
                "employee_id": "EMP999",
                "message": "How many leaves do I have?",
            },
        )
        assert response.status_code == 404

    def test_chat_empty_message(self):
        response = client.post(
            "/chat",
            json={
                "employee_id": "EMP001",
                "message": "",   # Empty — should fail Pydantic validation
            },
        )
        assert response.status_code == 422  # Unprocessable Entity


class TestEmployeeEndpoint:
    """Test the /employees/{employee_id} endpoint."""

    def test_get_existing_employee(self):
        response = client.get("/employees/EMP001")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == "EMP001"
        assert "name" in data
        assert "leave_balance" in data

    def test_get_nonexistent_employee(self):
        response = client.get("/employees/EMP999")
        assert response.status_code == 404


class TestConversationReset:
    """Test the conversation reset endpoint."""

    def test_reset_conversation(self):
        response = client.delete("/conversations/some-conv-id")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
