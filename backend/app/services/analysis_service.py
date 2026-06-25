"""
分析服务：完整的事件分析流水线 v2

集成 LLM 增强分析：
- sarcasm/homophone detection via LLM
- structured report generation per M8
"""

import json
from pathlib import Path
from typing import Any

from backend.app.algorithms.comment_graph import CommentGraphBuilder
from backend.app.algorithms.risk_scoring import RiskScoringEngine
from backend.app.algorithms.risk_signals import RiskSignalDetector
from backend.app.schemas.risk import RiskAssessment
from backend.app.services.embedding_service import EmbeddingService
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """分析服务 v2"""

    def __init__(
        self,
        use_embedding: bool = True,
        cache_dir: str = "./cache/demo_reports",
    ):
        self.use_embedding = use_embedding
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.signal_detector = RiskSignalDetector()
        self.graph_builder = CommentGraphBuilder()
        self.scoring_engine = RiskScoringEngine()
        self._embedding_service: EmbeddingService | None = None
        self._llm_service = None

    @property
    def embedding_service(self) -> EmbeddingService:
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    @property
    def llm_service(self):
        if self._llm_service is None:
            from backend.app.services.llm_service import get_llm_service
            self._llm_service = get_llm_service()
        return self._llm_service

    async def analyze_event(
        self,
        event: dict[str, Any],
        mode: str = "realtime",
        use_llm: bool = False,
    ) -> dict[str, Any]:
        """
        Analyze a single event with optional LLM enhancement

        Args:
            event: Event data with post and comments
            mode: "realtime" or "cached"
            use_llm: Whether to use LLM for enhanced analysis

        Returns:
            Analysis result dict
        """
        event_id = event.get("event_id", "")

        # Try cache first
        if mode == "cached":
            cached = self._load_from_cache(event_id)
            if cached:
                return cached

        # Step 1: Compute semantic embeddings
        if self.use_embedding:
            logger.info(f"[{event_id}] Computing embeddings...")
            event = self.embedding_service.encode_event(event, use_cache=True)

        # Step 2: Build comment graph
        logger.info(f"[{event_id}] Building comment graph...")
        graph = self.graph_builder.build_graph(event)
        centrality = self.graph_builder.compute_centrality(graph)

        # Step 3: Detect risk signals (with enhanced text cleaning + homophone/sarcasm)
        logger.info(f"[{event_id}] Detecting risk signals...")
        signals = self.signal_detector.detect_signals(
            event,
            use_semantic=self.use_embedding,
        )

        # Step 4: Enhanced sarcasm detection via LLM (for Top-N comments)
        llm_result = None
        if use_llm and self.llm_service.is_configured:
            try:
                # Collect Top-N comments by risk score for LLM analysis
                comments = event.get("comments", [])
                risky_comments = sorted(
                    [c for c in comments if c.get("text")],
                    key=lambda c: sum(
                        1 for s in signals
                        if s.comment_id == c.get("comment_id")
                    ),
                    reverse=True,
                )[:10]
                if risky_comments:
                    texts = [c["text"] for c in risky_comments]
                    llm_sarcasm = await self.llm_service.detect_sarcasm_and_homophones(
                        texts, use_cache=True
                    )
                    # Merge LLM sarcasm results into signals
                    for item in llm_sarcasm:
                        if item.get("has_covert_expression"):
                            idx = item.get("index", -1)
                            if 0 <= idx < len(risky_comments):
                                from backend.app.schemas.risk import RiskSignal
                                signals.append(RiskSignal(
                                    signal_type="sarcasm",
                                    comment_id=risky_comments[idx].get("comment_id"),
                                    evidence_text=risky_comments[idx]["text"][:80],
                                    score=item.get("confidence", 0.7),
                                    reason=f"LLM检测: {item.get('type', 'unknown')} - {item.get('explanation', '')}",
                                    source="llm",
                                ))
            except Exception as e:
                logger.warning(f"[{event_id}] LLM sarcasm detection failed: {e}")

        # Step 5: Compute risk score
        logger.info(f"[{event_id}] Computing risk score...")
        assessment = self.scoring_engine.compute_risk_score(
            event, signals, graph_centrality=centrality,
        )

        # Step 6: Build result
        comment_map = {c["comment_id"]: c.get("text", "") for c in event.get("comments", [])}

        result = {
            "event_id": event_id,
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "current_stage": assessment.current_stage,
            "evolution_path": assessment.evolution_path,
            "key_comments": assessment.key_comments,
            "risk_signals": [
                {
                    "signal_type": s.signal_type,
                    "comment_id": s.comment_id,
                    "evidence_text": s.evidence_text,
                    "comment_text": comment_map.get(s.comment_id, s.evidence_text),
                    "score": s.score,
                    "reason": s.reason,
                    "source": s.source,
                }
                for s in signals
            ],
            "graph": {
                "nodes": [n.model_dump() for n in graph.nodes],
                "edges": [e.model_dump() for e in graph.edges],
            },
            "confidence": assessment.confidence,
            "mode": "llm" if use_llm else mode,
            "llm_enhanced": use_llm and self.llm_service.is_configured,
        }

        # Cache the result
        self._save_to_cache(event_id, result)

        logger.info(f"[{event_id}] Analysis complete: {assessment.risk_level} (score: {assessment.risk_score:.2f})")

        return result

    def _load_from_cache(self, event_id: str) -> dict[str, Any] | None:
        cache_file = self.cache_dir / f"{event_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_to_cache(self, event_id: str, result: dict[str, Any]):
        cache_file = self.cache_dir / f"{event_id}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")


# Global singleton
_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service