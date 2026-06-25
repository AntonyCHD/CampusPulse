"""Report API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.app.services.analysis_service import get_analysis_service
from backend.app.services.rag_service import get_rag_service
from backend.app.storage.event_store import get_event_store

router = APIRouter(prefix="/api/report", tags=["report"])


def _build_key_comment_explanations(result: dict[str, Any]) -> list[dict[str, str]]:
    explanations = []
    signals = result.get("risk_signals", [])
    signal_lookup: dict[str, dict[str, Any]] = {}
    for signal in signals:
        comment_id = signal.get("comment_id") or signal.get("evidence_text")
        if comment_id:
            signal_lookup.setdefault(str(comment_id), signal)

    for comment_id in result.get("key_comments", []):
        signal = signal_lookup.get(str(comment_id))
        if signal:
            explanations.append(
                {
                    "comment_id": str(comment_id),
                    "reason": str(signal.get("reason", "")),
                    "risk_signal": str(signal.get("signal_type", "")),
                }
            )
        else:
            explanations.append(
                {
                    "comment_id": str(comment_id),
                    "reason": "被图谱中心性、点赞数和风险信号共同选为关键评论",
                    "risk_signal": "unknown",
                }
            )

    return explanations


@router.get("/{event_id}")
async def get_report(event_id: str):
    """获取事件报告"""
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    service = get_analysis_service()
    result = service.analyze_event(event, mode="cached", use_llm=False)

    rag_service = get_rag_service()
    evidence = [item.model_dump() for item in rag_service.retrieve(event, top_k=5)]
    key_comment_explanations = _build_key_comment_explanations(result)

    generated_at = datetime.now(timezone.utc)
    risk_level = result.get("risk_level")
    human_review_required = risk_level in {"高", "严重"} or bool(evidence)

    report = {
        "event_id": event_id,
        "event_summary": event.get("post", {}).get("text", "")[:100] + "...",
        "risk_assessment": {
            "risk_level": risk_level,
            "risk_score": result.get("risk_score"),
            "current_stage": result.get("current_stage"),
            "evolution_path": result.get("evolution_path"),
            "confidence": result.get("confidence"),
        },
        "key_findings": {
            "key_comments": result.get("key_comments", []),
            "risk_signals": result.get("risk_signals", []),
        },
        "key_comment_explanations": key_comment_explanations,
        "evidence": evidence,
        "intervention": {
            "summary": f"该事件处于'{result.get('current_stage')}'阶段，风险等级为'{risk_level}'。",
            "official_statement": "建议及时关注并回应学生诉求。",
            "action_items": ["核实情况", "发布说明", "跟进处理"],
            "avoid_phrases": ["请勿造谣", "不要再讨论"],
            "responsible_department": ["相关部门"],
            "urgency": "24小时内回应" if risk_level in ["高", "严重"] else "正常处理",
        },
        "human_review_required": human_review_required,
        "generated_at": generated_at,
        "mode": result.get("mode", "realtime"),
    }

    return report


@router.get("/{event_id}/export")
async def export_report(
    event_id: str,
    format: str = Query("md", description="导出格式: md/pdf"),
):
    """导出报告"""
    report = await get_report(event_id)

    if format == "md":
        evidence_lines = "\n".join(
            f"- {item['title']}（{item['source']}，得分 {item['score']:.2f}）"
            for item in report["evidence"]
        ) or "- 暂无证据"
        key_comment_lines = "\n".join(
            f"- {item['comment_id']}: {item['reason']} ({item['risk_signal']})"
            for item in report["key_comment_explanations"]
        ) or "- 暂无关键评论解释"

        md_content = f"""# 舆情分析报告

## 事件概况
- 事件ID: {report['event_id']}
- 事件摘要: {report['event_summary']}

## 风险评估
- 风险等级: {report['risk_assessment']['risk_level']}
- 风险分数: {report['risk_assessment']['risk_score']:.2f}
- 当前阶段: {report['risk_assessment']['current_stage']}
- 演化路径: {' → '.join(report['risk_assessment']['evolution_path'])}
- 需要人工复核: {'是' if report['human_review_required'] else '否'}

## 关键发现
- 关键评论数: {len(report['key_findings']['key_comments'])}
- 风险信号数: {len(report['key_findings']['risk_signals'])}

## 关键评论解释
{key_comment_lines}

## 证据链
{evidence_lines}

## 处置建议
{report['intervention']['summary']}

**建议行动:**
{chr(10).join(f'- {item}' for item in report['intervention']['action_items'])}

**避免话术:**
{chr(10).join(f'- {phrase}' for phrase in report['intervention']['avoid_phrases'])}

---
*报告生成时间: {report['generated_at'].isoformat()}*
"""
        return {"format": "md", "content": md_content}

    return {"format": format, "message": "PDF导出待实现"}
