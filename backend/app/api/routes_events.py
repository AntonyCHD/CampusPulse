"""Events API routes."""

from collections import Counter, defaultdict
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from backend.app.storage.event_store import get_event_store

router = APIRouter(prefix="/api/events", tags=["events"])

HIGH_RISK_LEVELS = {"高", "严重"}
RISK_LEVELS = ("低", "中", "高", "严重")


def _date_key(value: str | None) -> str:
    if not value:
        return "未知"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value[:10] if len(value) >= 10 else "未知"


@router.get("/")
async def list_events(
    risk_level: str | None = Query(None, description="筛选风险等级"),
    event_type: str | None = Query(None, description="筛选事件类型"),
    limit: int = Query(100, ge=1, le=200, description="返回数量限制"),
):
    """获取事件列表（带缓存的风险等级和总览统计）"""
    from backend.app.services.analysis_service import get_analysis_service

    store = get_event_store()
    events = store.get_all_events(
        risk_level=risk_level,
        event_type=event_type,
        limit=limit,
    )

    analysis_service = get_analysis_service()

    items = []
    risk_counter: Counter[str] = Counter({level: 0 for level in RISK_LEVELS})
    type_counter: Counter[str] = Counter()
    trend: dict[str, dict[str, float | int]] = defaultdict(lambda: {"count": 0, "avg_risk_score": 0.0})

    for event in events:
        event_id = event.get("event_id")
        cached = analysis_service._load_from_cache(event_id)
        if cached:
            risk_level_val = cached.get("risk_level", "低")
            risk_score_val = float(cached.get("risk_score", 0.0))
        else:
            risk_level_val = "低"
            risk_score_val = 0.0

        if risk_level and risk_level_val != risk_level:
            continue

        created_at = event.get("post", {}).get("created_at")
        date = _date_key(created_at)
        event_type_val = event.get("event_type") or "其他"

        risk_counter[risk_level_val] += 1
        type_counter[event_type_val] += 1
        trend[date]["count"] = int(trend[date]["count"]) + 1
        trend[date]["avg_risk_score"] = float(trend[date]["avg_risk_score"]) + risk_score_val

        items.append({
            "event_id": event_id,
            "event_type": event_type_val,
            "title": event.get("post", {}).get("text", "")[:50] + "...",
            "comment_count": len(event.get("comments", [])),
            "like_count": event.get("post", {}).get("like_count", 0),
            "created_at": created_at,
            "risk_level": risk_level_val,
            "risk_score": risk_score_val,
        })

    risk_trend = []
    for date, values in sorted(trend.items()):
        count = int(values["count"])
        total_score = float(values["avg_risk_score"])
        risk_trend.append({
            "date": date,
            "count": count,
            "avg_risk_score": round(total_score / count, 2) if count else 0.0,
        })

    today = datetime.now().date().isoformat()
    summary = {
        "total_events": len(items),
        "today_events": sum(1 for item in items if _date_key(item.get("created_at")) == today),
        "high_risk_events": sum(1 for item in items if item.get("risk_level") in HIGH_RISK_LEVELS),
        "risk_distribution": dict(risk_counter),
        "event_type_distribution": dict(type_counter),
        "risk_trend": risk_trend,
    }

    return {
        "items": items,
        "total": len(items),
        "summary": summary,
    }


@router.get("/{event_id}")
async def get_event(event_id: str):
    """获取单个事件详情"""
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    return event
