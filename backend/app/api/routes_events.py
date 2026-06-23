"""Events API routes."""

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/")
async def list_events(
    risk_level: str | None = Query(None, description="筛选风险等级"),
    event_type: str | None = Query(None, description="筛选事件类型"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
):
    """获取事件列表"""
    # TODO: Implement event listing logic
    return {
        "items": [],
        "total": 0,
        "message": "事件列表接口待实现",
    }


@router.get("/{event_id}")
async def get_event(event_id: str):
    """获取单个事件详情"""
    # TODO: Implement event retrieval logic
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
