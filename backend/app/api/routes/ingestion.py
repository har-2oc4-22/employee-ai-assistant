"""
api/routes/ingestion.py
------------------------
POST /ingest — trigger document ingestion.

Protected by a simple secret key so it cannot be triggered by random users.
In production, this would require admin authentication.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from app.config import settings
from app.models.chat import IngestRequest
from app.rag.ingestion import ingest_documents

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    tags=["Administration"],
    summary="Trigger document ingestion into ChromaDB",
)
async def trigger_ingestion(request: IngestRequest) -> dict:
    """
    Reads documents from the documents directory, chunks them,
    generates embeddings, and stores them in ChromaDB.

    Protected by a secret key (INGEST_SECRET in .env).
    Pass force_reingest=true to re-embed all documents from scratch.
    """
    if request.secret != settings.INGEST_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid ingest secret.",
        )

    logger.info(
        "POST /ingest triggered | force_reingest=%s", request.force_reingest
    )

    try:
        result = await run_in_threadpool(
            ingest_documents,
            settings.DOCUMENTS_DIR,
            request.force_reingest,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Ingestion failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document ingestion failed. Check backend logs for details.",
        )
