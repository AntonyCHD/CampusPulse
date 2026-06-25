"""Graph API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.app.services.analysis_service import get_analysis_service
from backend.app.services.graph_visualizer import get_graph_visualizer
from backend.app.storage.event_store import get_event_store

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/{event_id}")
async def get_event_graph(event_id: str):
    """获取事件评论图谱"""
    # 获取事件
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    # 尝试从缓存加载分析结果
    service = get_analysis_service()
    cached = service._load_from_cache(event_id)

    if cached and "graph" in cached:
        return cached["graph"]

    # 如果没有缓存，先执行分析
    result = service.analyze_event(event, mode="realtime", use_llm=False)
    return result.get("graph", {"nodes": [], "edges": []})


@router.post("/{event_id}/render")
async def render_graph(event_id: str, graph_data: dict[str, Any]):
    """渲染图谱为 HTML"""
    visualizer = get_graph_visualizer()

    try:
        html_path = visualizer.render_graph(graph_data, event_id)
        return {"html_path": html_path, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"渲染失败: {e}")
