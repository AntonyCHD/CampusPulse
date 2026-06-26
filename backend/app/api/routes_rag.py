"""RAG status API route."""

from fastapi import APIRouter

from backend.app.services.rag_service import get_rag_service

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.get("/status")
async def rag_status():
    """Return RAG system status including vector store connectivity and document count."""
    rag = get_rag_service()
    return rag.get_status()
