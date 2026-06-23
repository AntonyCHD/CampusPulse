"""Report API routes."""

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/{event_id}")
async def get_report(event_id: str):
    """获取事件报告"""
    # TODO: Implement report retrieval logic
    raise HTTPException(status_code=404, detail=f"Report for event {event_id} not found")


@router.get("/{event_id}/export")
async def export_report(
    event_id: str,
    format: str = Query("md", description="导出格式: md/pdf"),
):
    """导出报告"""
    # TODO: Implement report export logic
    return {
        "event_id": event_id,
        "format": format,
        "message": "报告导出接口待实现",
    }
