"""Analysis API routes."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/analyze", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    """分析请求"""

    mode: str = "realtime"  # realtime / cached
    use_llm: bool = True
    use_rag: bool = True
    top_n_comments: int = 20


@router.post("/{event_id}")
async def analyze_event(event_id: str, request: AnalyzeRequest):
    """运行完整分析流水线"""
    # TODO: Implement analysis logic
    return {
        "event_id": event_id,
        "message": "分析接口待实现",
        "request": request.model_dump(),
    }
