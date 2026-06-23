"""Baseline comparison API routes."""

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/baseline", tags=["baseline"])


@router.post("/{event_id}")
async def run_baseline(
    event_id: str,
    method: str = Query("keyword", description="基线方法: keyword/sentiment"),
):
    """运行基线方法对比"""
    # TODO: Implement baseline comparison logic
    return {
        "event_id": event_id,
        "method": method,
        "message": "基线对比接口待实现",
    }
