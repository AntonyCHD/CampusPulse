"""Report API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.app.services.analysis_service import get_analysis_service
from backend.app.services.rag_service import get_rag_service
from backend.app.storage.event_store import get_event_store
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

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



def _build_intervention_rules(
    result: dict[str, Any],
    event: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Rule-based intervention generation (LLM fallback)."""
    risk_level = result.get("risk_level", "中")
    current_stage = result.get("current_stage", "信息求证")
    event_type = event.get("event_type", "")

    dept_keywords = {
        "饮食服务中心": ["食堂", "餐饮", "档口", "菜品", "价格"],
        "学生公寓管理中心": ["宿舍", "住宿", "暖气", "水电", "门禁"],
        "后勤保障处": ["后勤", "维修", "设施", "厕所", "卫生"],
        "学生工作部": ["学生", "权益", "申诉", "投诉", "辅导员"],
        "党委宣传部": ["舆情", "网络", "意见"],
        "保卫处": ["安全", "保卫"],
    }
    evidence_text = " ".join(e.get("content", "") for e in evidence)
    event_text = event.get("post", {}).get("text", "") + " " + event_type

    responsible = []
    for dept, keywords in dept_keywords.items():
        if any(kw in evidence_text or kw in event_text for kw in keywords):
            responsible.append(dept)
    if not responsible:
        responsible = ["学生工作部", "后勤保障处"]

    templates = [e for e in evidence if e.get("evidence_type") == "response_template"]
    if templates:
        best = max(templates, key=lambda e: e.get("score", 0))
        content_lines = [l.strip() for l in best.get("content", "").split("\n")
                         if l.strip() and not l.startswith("#")]
        stmt = [l for l in content_lines
                if not l.startswith("##") and not l.startswith("- ")
                and len(l) > 20][:2]
        official_statement = "；".join(stmt) if stmt else "请参照相应模板准备正式回应。"
    else:
        policies = [e for e in evidence if e.get("evidence_type") == "policy"]
        if policies:
            best = max(policies, key=lambda e: e.get("score", 0))
            official_statement = f"根据{best.get('title', '相关规定')}，建议核实情况后参照制度要求进行回应。"
        else:
            official_statement = "建议及时关注并回应学生诉求，避免问题升级。"

    action_items = ["核实事件事实与影响范围"]
    if risk_level in ("高", "严重"):
        action_items.append("启动24小时应急响应机制")
    if current_stage in ("信息求证", "个体吐槽"):
        action_items.append("通过官方渠道发布事实说明")
    if current_stage in ("集体共鸣", "立场对立"):
        action_items.append("组织相关部门与学生代表座谈沟通")
    if risk_level in ("高", "严重") and current_stage in ("组织化行动", "线下风险"):
        action_items.append("安排辅导员进行一对一温和沟通")
    for ev in evidence:
        if "反馈渠道" in ev.get("content", ""):
            action_items.append("公布问题反馈与投诉渠道")
            break
    action_items.append("记录处置过程并归档总结")

    avoid_phrases = ["请勿造谣", "不要再讨论", "你们不懂", "这是规定", "不关学校的事"]
    if risk_level == "严重":
        urgency = "立即启动应急预案，2小时内首次回应"
    elif risk_level == "高":
        urgency = "24小时内回应并发布进展说明"
    elif current_stage in ("集体共鸣", "立场对立"):
        urgency = "48小时内发布情况说明"
    else:
        urgency = "72小时内关注并评估"

    summary = (
        f"事件处于{chr(39)}{current_stage}{chr(39)}阶段，风险等级为{chr(39)}{risk_level}{chr(39)}。"
        f"已检索到 {len(evidence)} 条相关制度/模板证据。"
        f"建议由{', '.join(responsible[:3])}牵头处置。"
    )
    return {
        "summary": summary,
        "official_statement": official_statement,
        "action_items": action_items,
        "avoid_phrases": avoid_phrases,
        "responsible_department": responsible,
        "urgency": urgency,
        "human_review_required": risk_level in ("高", "严重") or bool(evidence),
    }


async def _build_intervention_llm(
    result: dict[str, Any],
    event: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Try LLM-based intervention. Returns None if LLM unavailable."""
    try:
        from backend.app.services.llm_service import get_llm_service
        llm = get_llm_service()
        if not llm.is_configured:
            return None
    except Exception:
        return None

    import json as json_mod

    risk_level = result.get("risk_level", "中")
    current_stage = result.get("current_stage", "")
    event_type = event.get("event_type", "")
    event_title = event.get("post", {}).get("title", "")
    event_text = event.get("post", {}).get("text", "")[:300]

    signals_summary = []
    for s in result.get("risk_signals", [])[:10]:
        signals_summary.append({
            "type": s.get("signal_type", ""),
            "evidence": s.get("evidence_text", "")[:80],
            "reason": s.get("reason", ""),
        })

    evidence_summary = []
    for e in evidence:
        evidence_summary.append({
            "title": e.get("title", ""),
            "source": e.get("source", ""),
            "type": e.get("evidence_type", ""),
            "excerpt": e.get("content", "")[:300],
        })

    system_prompt = (
        "你是中国传媒大学舆情处置顾问。基于校园舆情分析数据和知识库检索到的制度/模板证据，"
        "生成具体的、可执行的温和处置方案。要求：1.回应话术温和、承认学生感受、不压制表达 "
        "2.行动项具体可验证有时限 3.避免话术符合校园语境 4.责任部门匹配实际组织结构 "
        "5.处置时限匹配风险等级。仅输出 JSON，不含 markdown 代码块标记。"
    )

    evolution_path = result.get("evolution_path", [])
    user_prompt = (
        f"## 事件信息\n"
        f"- 类型：{event_type}\n"
        f"- 标题：{event_title}\n"
        f"- 摘要：{event_text}\n\n"
        f"## 分析结果\n"
        f"- 风险等级：{risk_level}\n"
        f"- 当前阶段：{current_stage}\n"
        f"- 演化路径：{' -> '.join(evolution_path)}\n\n"
        f"## 风险信号\n"
        f"{json_mod.dumps(signals_summary, ensure_ascii=False, indent=2)}\n\n"
        f"## 知识库证据\n"
        f"{json_mod.dumps(evidence_summary, ensure_ascii=False, indent=2)}\n\n"
        f"请输出 JSON：\n"
        f'{{"summary":"...","official_statement":"...","action_items":[...],'
        f'"avoid_phrases":[...],"responsible_department":[...],"urgency":"...",'
        f'"human_review_required":true/false}}'
    )

    try:
        llm_result = await llm.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
            response_format={"type": "json_object"},
            use_cache=True,
        )
        content_resp = llm_result["choices"][0]["message"]["content"]
        parsed = json_mod.loads(content_resp)
        # Normalize action_items: if LLM returns objects, convert to strings
        raw_actions = parsed.get("action_items", ["核实", "发布"])
        if raw_actions and isinstance(raw_actions[0], dict):
            action_items = [
                f'{a.get("task", "")} ({a.get("responsible", "")}, {a.get("deadline", "")})'
                for a in raw_actions
            ]
        else:
            action_items = raw_actions

        return {
            "summary": parsed.get("summary", f"风险等级{risk_level}"),
            "official_statement": parsed.get("official_statement", "关注并回应学生诉求。"),
            "action_items": action_items,
            "avoid_phrases": parsed.get("avoid_phrases", []),
            "responsible_department": parsed.get("responsible_department", ["学生工作部"]),
            "urgency": parsed.get("urgency", "48小时内") if isinstance(parsed.get("urgency", ""), str) else "48小时内",
            "human_review_required": parsed.get("human_review_required", risk_level in ("高", "严重")),
        }
    except Exception as e:
        logger.warning(f"LLM intervention failed, falling back to rules: {e}")
        return None


async def _get_intervention(
    result: dict[str, Any],
    event: dict[str, Any],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Get intervention advice: LLM first, then rules fallback."""
    llm_result = await _build_intervention_llm(result, event, evidence)
    if llm_result is not None:
        return llm_result
    rules_result = _build_intervention_rules(result, event, evidence)
    return rules_result


@router.get("/{event_id}")
async def get_report(event_id: str):
    """获取事件报告"""
    store = get_event_store()
    event = store.get_event(event_id)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    service = get_analysis_service()
    result = await service.analyze_event(event, mode="cached", use_llm=False)

    rag_service = get_rag_service()
    evidence = [item.model_dump() for item in rag_service.retrieve(event, top_k=5)]
    key_comment_explanations = _build_key_comment_explanations(result)

    generated_at = datetime.now(timezone.utc)
    risk_level = result.get("risk_level")

    # LLM-first intervention, rule fallback
    intervention = await _get_intervention(result, event, evidence)
    human_review_required = intervention.pop("human_review_required", risk_level in {"高", "严重"} or bool(evidence))

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
        "intervention": intervention,
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
