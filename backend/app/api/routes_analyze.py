"""Analysis API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.analysis_service import get_analysis_service
from backend.app.storage.event_store import get_event_store

router = APIRouter(prefix="/api/analyze", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    """分析请求"""

    mode: str = "realtime"  # realtime / cached
    use_llm: bool = False
    use_rag: bool = False
    comment_topn: int = 20
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"


@router.post("/{event_id}")
async def analyze_event(event_id: str, request: AnalyzeRequest | None = None):
    """运行完整分析流水线"""
    if request is None:
        request = AnalyzeRequest()

    # Get event data
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    service = get_analysis_service()

    # Try cache first for non-LLM mode
    if request.mode == "cached" and not request.use_llm:
        cached = service._load_from_cache(event_id)
        if cached:
            return cached

    # Run analysis (async for LLM support)
    result = await service.analyze_event(
        event,
        mode=request.mode,
        use_llm=request.use_llm,
    )

    return result