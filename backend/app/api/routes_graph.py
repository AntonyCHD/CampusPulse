"""Graph API routes."""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/{event_id}")
async def get_event_graph(event_id: str):
    """获取事件评论图谱"""
    # TODO: Implement graph retrieval logic
    raise HTTPException(status_code=404, detail=f"Graph for event {event_id} not found")
