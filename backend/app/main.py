"""
main.py
--------
FastAPI application entry point.

This file:
  1. Creates the FastAPI app instance.
  2. Configures CORS (so the React frontend can make requests).
  3. Registers all route routers.
  4. Sets up logging.
  5. Validates critical settings on startup.
  6. Registers a global exception handler.
"""

import logging
import sys
from contextlib import asynccontextmanager

# ── Ensure UTF-8 output on Windows console ───────────────────────────────────
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, health, ingestion
from app.config import settings

# ── Logging setup ────────────────────────────────────────────────────────────
# Use structured logging format with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown events) ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler.
    Code before `yield` runs on startup.
    Code after `yield` runs on shutdown.
    """
    # Validate that GEMINI_API_KEY is set — fail fast rather than on first request
    try:
        settings.validate()
        logger.info("✅ Configuration validated.")
    except ValueError as e:
        logger.critical("❌ Configuration error: %s", e)
        sys.exit(1)

    logger.info("🚀 Employee AI Assistant starting up...")
    logger.info("   Chat model:       %s", settings.GEMINI_CHAT_MODEL)
    logger.info("   Embedding model:  %s", settings.GEMINI_EMBEDDING_MODEL)
    logger.info("   ChromaDB path:    %s", settings.CHROMA_PERSIST_DIRECTORY)
    logger.info("   Documents dir:    %s", settings.DOCUMENTS_DIR)
    logger.info("   Frontend origin:  %s", settings.FRONTEND_ORIGIN)

    yield  # Application is running

    logger.info("👋 Employee AI Assistant shutting down.")


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Employee AI Assistant",
    description=(
        "RAG + Agentic Employee Assistant — helps employees with company policies, "
        "employee information, and leave management."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)


# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the React frontend (http://localhost:5173) to call the API.
# In production, set FRONTEND_ORIGIN to your production URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(ingestion.router)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for any unhandled exceptions.
    Returns a clean JSON error to the frontend — never a raw stack trace.
    """
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.url.path, exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please contact support."},
    )


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Employee AI Assistant API",
        "docs": "/docs",
        "health": "/health",
    }
