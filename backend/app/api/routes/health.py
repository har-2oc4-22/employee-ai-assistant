"""
api/routes/health.py
---------------------
GET /health — simple liveness check endpoint.
Used by load balancers and monitoring tools to verify the API is up.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Returns 200 OK with status 'ok' if the backend is running.
    Does NOT check ChromaDB or Gemini connectivity (that would make it a readiness probe).
    """
    return HealthResponse(status="ok", message="Employee AI Assistant is running.")
