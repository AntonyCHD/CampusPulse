"""RAG evidence retrieval using BGE-M3 embeddings and Milvus vector store.

Replaces the earlier hardcoded rule-based retriever with real semantic search.
When Milvus is unavailable or the collection is empty, falls back gracefully
to the rule-based approach.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from backend.app.schemas.evidence import Evidence
from backend.app.services.embedding_service import EmbeddingService
from backend.app.storage.vector_store import MilvusVectorStore
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class RagService:
    """Semantic evidence retrieval backed by BGE-M3 + Milvus.

    Uses the vector store for primary retrieval and falls back to the
    legacy rule-based approach when the vector store is empty or unreachable.
    """

    def __init__(self) -> None:
        self._vector_store: MilvusVectorStore | None = None
        self._embedding_service: EmbeddingService | None = None
        self._connected: bool | None = None  # None = not tried yet

    @property
    def vector_store(self) -> MilvusVectorStore:
        if self._vector_store is None:
            self._vector_store = MilvusVectorStore()
        return self._vector_store

    @property
    def embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    def _ensure_connected(self) -> bool:
        """Lazily connect to Milvus and cache the result."""
        if self._connected is None:
            self._connected = self.vector_store.connect()
            if self._connected:
                count = self.vector_store.get_count()
                logger.info(f"Milvus connected, collection has {count} documents")
                if count == 0:
                    logger.warning("Milvus collection is empty; RAG will fall back to rules")
            else:
                logger.warning("Milvus not available; RAG will fall back to rules")
        return self._connected

    def retrieve(
        self,
        event: dict[str, Any],
        top_k: int = 5,
    ) -> list[Evidence]:
        """Retrieve evidence for an event.

        Primary: semantic search via BGE-M3 + Milvus.
        Fallback: rule-based keyword matching.
        """
        # Try vector search first
        if self._ensure_connected() and self.vector_store.get_count() > 0:
            return self._retrieve_vector(event, top_k)

        # Fall back to rule-based
        logger.info("Using rule-based fallback for evidence retrieval")
        return self._retrieve_rules(event, top_k)

    def _retrieve_vector(
        self,
        event: dict[str, Any],
        top_k: int = 5,
    ) -> list[Evidence]:
        """Semantic retrieval using BGE-M3 embedding + Milvus search."""
        query_text = self._build_query_text(event)
        if not query_text.strip():
            return []

        # Generate embedding for the query
        query_embedding = self.embedding_service.encode(query_text, use_cache=True)

        # Search Milvus
        hits = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            top_k=top_k,
        )

        evidence_list = []
        for hit in hits:
            evidence_list.append(Evidence(
                evidence_id=hit["evidence_id"],
                title=hit["title"],
                source=hit["source"],
                content=hit["content"][:500],
                score=hit["score"],
                evidence_type=hit["evidence_type"],
            ))

        logger.info(
            f"Vector retrieval returned {len(evidence_list)} results "
            f"(top score: {evidence_list[0].score:.3f})"
            if evidence_list else "Vector retrieval returned 0 results"
        )
        return evidence_list

    def _retrieve_rules(
        self,
        event: dict[str, Any],
        top_k: int = 5,
    ) -> list[Evidence]:
        """Legacy rule-based retrieval as fallback."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class EvidenceRule:
            evidence_id: str
            title: str
            source: str
            content: str
            evidence_type: str
            keywords: tuple[str, ...]
            priority: float

        rules = (
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

        query_text = self._build_query_text(event)
        ranked: list[Evidence] = []

        for rule in rules:
            hit_count = sum(1 for kw in rule.keywords if kw in query_text)
            type_bonus = 0.08 if event.get("event_type") and event.get("event_type") in rule.content else 0.0
            score = min(1.0, rule.priority * (0.45 + 0.13 * hit_count) + type_bonus)
            if hit_count > 0 or rule.evidence_id == "policy_student_appeal":
                ranked.append(Evidence(
                    evidence_id=rule.evidence_id,
                    title=rule.title,
                    source=rule.source,
                    content=rule.content,
                    score=round(score, 3),
                    evidence_type=rule.evidence_type,
                ))

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
        parts.extend(str(c.get("text", "")) for c in comments[:20])
        return " ".join(p for p in parts if p)

    def get_status(self) -> dict[str, Any]:
        """Return the current RAG status."""
        connected = self._ensure_connected()
        count = self.vector_store.get_count() if connected else 0
        return {
            "mode": "vector" if (connected and count > 0) else "rule_fallback",
            "milvus_connected": connected,
            "document_count": count,
            "collection": "campus_knowledge_base",
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_rag_service: RagService | None = None


def get_rag_service() -> RagService:
    """Return the process-wide RAG service singleton."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service
