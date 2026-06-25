"""Baseline comparison API routes."""

from fastapi import APIRouter, HTTPException, Query

from backend.app.services.analysis_service import get_analysis_service
from backend.app.services.baseline_service import get_baseline_service
from backend.app.storage.event_store import get_event_store

router = APIRouter(prefix="/api/baseline", tags=["baseline"])


@router.post("/{event_id}")
async def run_baseline(
    event_id: str,
    method: str = Query("keyword", description="基线方法: keyword/sentiment/all"),
):
    """运行基线方法对比"""
    # 获取事件
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    # 运行评论链方法（我们的方法）
    analysis_service = get_analysis_service()
    our_result = analysis_service.analyze_event(event, mode="cached", use_llm=False)

    # 运行基线方法
    baseline_service = get_baseline_service()

    results = {
        "event_id": event_id,
        "comment_chain_method": {
            "method": "评论链演化法",
            "risk_level": our_result.get("risk_level"),
            "risk_score": our_result.get("risk_score"),
            "reason": f"基于评论链分析，当前阶段：{our_result.get('current_stage')}",
            "details": {
                "signals": len(our_result.get("risk_signals", [])),
                "key_comments": our_result.get("key_comments", []),
            },
        },
    }

    if method in ["keyword", "all"]:
        results["keyword_method"] = baseline_service.keyword_method(event)

    if method in ["sentiment", "all"]:
        results["sentiment_method"] = baseline_service.sentiment_method(event)

    return results
