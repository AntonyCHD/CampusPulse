"""Rule-backed evidence retrieval for demo-mode RAG.

The first production version intentionally uses a curated local rule base. It
keeps the report pipeline evidence-grounded without depending on external vector
stores or a live knowledge base during the course demo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.schemas.evidence import Evidence


@dataclass(frozen=True)
class EvidenceRule:
    evidence_id: str
    title: str
    source: str
    content: str
    evidence_type: str
    keywords: tuple[str, ...]
    priority: float


class RagService:
    """Small deterministic evidence retriever for MVP/demo use."""

    def __init__(self) -> None:
        self.rules: tuple[EvidenceRule, ...] = (
            EvidenceRule(
                evidence_id="policy_dorm_appeal",
                title="宿舍管理诉求处理流程",
                source="校内后勤处置模板",
                content="涉及宿舍断电、维修、门禁等后勤问题时，应先核实通知来源与影响范围，再由后勤或宿管渠道发布说明并给出补救安排。",
                evidence_type="policy",
                keywords=("宿舍", "断电", "门禁", "后勤", "楼下", "维修"),
                priority=0.95,
            ),
            EvidenceRule(
                evidence_id="notice_logistics_response",
                title="后勤服务争议回应模板",
                source="校内回应话术库",
                content="回应应承认学生实际不便，说明核查进展、临时安排和反馈渠道，避免使用压制讨论或归责学生的话术。",
                evidence_type="response_template",
                keywords=("后勤", "食堂", "价格", "宿舍", "不便", "回应"),
                priority=0.88,
            ),
            EvidenceRule(
                evidence_id="policy_student_appeal",
                title="学生诉求反馈与复核渠道",
                source="学生工作处置规范",
                content="对事实未明或争议较高的事件，应提供线上反馈入口、责任部门和预计回复时限，并保留人工复核。",
                evidence_type="policy",
                keywords=("投诉", "举报", "求证", "通知", "不清楚", "复核"),
                priority=0.84,
            ),
            EvidenceRule(
                evidence_id="sop_mobilization",
                title="线下聚集风险处置提示",
                source="舆情处置SOP",
                content="出现明确时间、地点、集合或集体询问表达时，应在24小时内核实现场风险，安排辅导员或相关部门温和沟通。",
                evidence_type="history_case",
                keywords=("一起", "集合", "今晚", "明天", "门口", "楼下", "去问"),
                priority=0.92,
            ),
            EvidenceRule(
                evidence_id="template_rumor_clarification",
                title="传闻求证澄清模板",
                source="校内澄清模板",
                content="面对听说、据说、可能等未证实信息，应区分事实、正在核查事项和暂无依据内容，避免扩大不确定性。",
                evidence_type="response_template",
                keywords=("听说", "据说", "好像", "可能", "真的假的", "谣言"),
                priority=0.8,
            ),
        )

    def retrieve(self, event: dict[str, Any], top_k: int = 5) -> list[Evidence]:
        """Return ranked evidence snippets for an event."""
        query_text = self._build_query_text(event)
        ranked: list[Evidence] = []

        for rule in self.rules:
            hit_count = sum(1 for keyword in rule.keywords if keyword in query_text)
            type_bonus = 0.08 if event.get("event_type") and event.get("event_type") in rule.content else 0.0
            score = min(1.0, rule.priority * (0.45 + 0.13 * hit_count) + type_bonus)
            if hit_count > 0 or rule.evidence_id == "policy_student_appeal":
                ranked.append(
                    Evidence(
                        evidence_id=rule.evidence_id,
                        title=rule.title,
                        source=rule.source,
                        content=rule.content,
                        score=round(score, 3),
                        evidence_type=rule.evidence_type,
                    )
                )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[: max(1, top_k)]

    def _build_query_text(self, event: dict[str, Any]) -> str:
        post = event.get("post", {})
        comments = event.get("comments", [])
        parts = [
            str(event.get("event_type", "")),
            str(post.get("title", "")),
            str(post.get("text", "")),
            str(post.get("clean_text", "")),
        ]
        parts.extend(str(comment.get("text", "")) for comment in comments[:20])
        return " ".join(part for part in parts if part)


_rag_service: RagService | None = None


def get_rag_service() -> RagService:
    """Return the process-wide RAG service."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service
