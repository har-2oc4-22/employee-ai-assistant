"""
api/routes/chat.py
-------------------
POST /chat — main chat endpoint.
GET  /employees/{employee_id} — employee info lookup.
DELETE /conversations/{conversation_id} — reset conversation.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.agent.state import clear_history
from app.models.chat import ChatRequest, ChatResponse
from app.models.employee import Employee
from app.services.chat_service import process_chat
from app.services.employee_service import get_employee

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Send a message to the AI assistant",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.

    Accepts a user message and returns the AI assistant's response.
    Include conversation_id in subsequent requests to maintain context.
    """
    logger.info(
        "POST /chat | emp=%s | conv=%s | msg='%s'",
        request.employee_id,
        request.conversation_id,
        request.message[:80],
    )

    # Validate employee exists before hitting the agent
    employee = await run_in_threadpool(get_employee, request.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee ID '{request.employee_id}' not found. Please check your employee ID.",
        )

    try:
        # run_in_threadpool so the synchronous agent doesn't block FastAPI's event loop
        response = await run_in_threadpool(
            process_chat,
            request.employee_id,
            request.message,
            request.conversation_id,
        )
        return response
    except ValueError as e:
        logger.warning("Validation error in /chat: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error in /chat: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again.",
        )


@router.get(
    "/employees/{employee_id}",
    response_model=Employee,
    tags=["Employees"],
    summary="Get employee information",
)
async def get_employee_info(employee_id: str) -> Employee:
    """
    Fetch an employee's details by ID.
    Useful for testing and debugging.
    """
    employee = await run_in_threadpool(get_employee, employee_id.upper())
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found.",
        )
    return employee


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Reset conversation history",
)
async def reset_conversation(conversation_id: str) -> dict:
    """
    Delete the conversation history for the given conversation_id.
    Use this when the user wants to start a fresh conversation.
    """
    clear_history(conversation_id)
    return {"status": "ok", "message": f"Conversation '{conversation_id}' has been reset."}
