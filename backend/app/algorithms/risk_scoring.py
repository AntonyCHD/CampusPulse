"""
风险评分算法

综合多个因素计算风险分数：
- 主贴风险 (20%)
- 情绪共振 (25%)
- 行动号召强度 (20%)
- 图结构影响力 (15%)
- 突增程度 (10%)
- 事实不确定性 (10%)

风险等级：
- 0-39: 低
- 40-64: 中
- 65-84: 高
- 85-100: 严重
"""

from typing import Any

import numpy as np

from backend.app.schemas.enums import EvolutionStage, RiskLevel
from backend.app.schemas.risk import RiskAssessment, RiskSignal


class RiskScoringEngine:
    """风险评分引擎"""

    def __init__(self):
        """初始化评分引擎"""
        # 权重配置
        self.weights = {
            "post_risk": 0.20,
            "resonance": 0.25,
            "mobilization": 0.20,
            "graph_influence": 0.15,
            "burst": 0.10,
            "uncertainty": 0.10,
        }

    def compute_risk_score(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
        graph_centrality: dict[str, float] | None = None,
    ) -> RiskAssessment:
        """
        计算综合风险评分

        Args:
            event: 事件数据
            signals: 风险信号列表
            graph_centrality: 节点中心性分数

        Returns:
            风险评估结果
        """
        # 计算各项分数
        post_risk = self._compute_post_risk(event, signals)
        resonance = self._compute_resonance_score(event, signals)
        mobilization = self._compute_mobilization_score(signals)
        graph_influence = self._compute_graph_influence(
            event, signals, graph_centrality
        )
        burst = self._compute_burst_score(event)
        uncertainty = self._compute_uncertainty_score(signals)

        # 综合评分
        risk_score = (
            self.weights["post_risk"] * post_risk
            + self.weights["resonance"] * resonance
            + self.weights["mobilization"] * mobilization
            + self.weights["graph_influence"] * graph_influence
            + self.weights["burst"] * burst
            + self.weights["uncertainty"] * uncertainty
        )

        # 归一化到 0-100
        risk_score = min(100.0, max(0.0, risk_score * 100))

        # 判断风险等级
        risk_level = self._map_score_to_level(risk_score)

        # 判断演化阶段
        current_stage, evolution_path = self._infer_evolution_stage(
            event, signals, resonance
        )

        # 识别关键评论
        key_comments = self._identify_key_comments(event, signals, graph_centrality)

        return RiskAssessment(
            event_id=event.get("event_id", ""),
            risk_level=risk_level,
            risk_score=risk_score,
            current_stage=current_stage,
            evolution_path=evolution_path,
            key_comments=key_comments,
            risk_signals=signals,
            confidence=self._compute_confidence(signals),
        )

    def _compute_post_risk(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
    ) -> float:
        """计算主贴风险分数 (0-1)"""
        post_signals = [s for s in signals if s.comment_id is None]

        if not post_signals:
            return 0.4  # 基础分

        # 取最高分
        max_score = max(s.score for s in post_signals)
        return max_score

    def _compute_resonance_score(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
    ) -> float:
        """计算情绪共振分数 (0-1)"""
        comments = event.get("comments", [])
        if not comments:
            return 0.0

        # 负面评论比例
        negative_signals = [
            s for s in signals if s.signal_type == "negative_emotion"
        ]
        negative_ratio = len(negative_signals) / max(1, len(comments))

        # 集体共鸣信号
        resonance_signals = [
            s for s in signals if s.signal_type == "collective_resonance"
        ]
        has_resonance = len(resonance_signals) > 0

        # 高点赞评论比例
        total_likes = sum(c.get("like_count", 0) for c in comments)
        if total_likes > 0:
            negative_likes = sum(
                event.get("comments", [])[i].get("like_count", 0)
                for i, s in enumerate(signals)
                if s.signal_type == "negative_emotion" and s.comment_id
            )
            interaction_amp = negative_likes / total_likes
        else:
            interaction_amp = 0.0

        # 综合计算
        score = (
            0.30 * negative_ratio
            + 0.40 * (1.0 if has_resonance else 0.0)
            + 0.30 * interaction_amp
        )

        return min(1.0, score)

    def _compute_mobilization_score(self, signals: list[RiskSignal]) -> float:
        """计算行动号召强度 (0-1)"""
        mobilization_signals = [
            s for s in signals if s.signal_type == "mobilization"
        ]

        if not mobilization_signals:
            return 0.0

        # 取最高分，并考虑数量
        max_score = max(s.score for s in mobilization_signals)
        count_bonus = min(0.2, len(mobilization_signals) * 0.05)

        return min(1.0, max_score + count_bonus)

    def _compute_graph_influence(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
        graph_centrality: dict[str, float] | None,
    ) -> float:
        """计算图结构影响力 (0-1)"""
        if not graph_centrality:
            return 0.6  # 默认中等影响力

        # 找出有风险信号的评论
        risk_comment_ids = {s.comment_id for s in signals if s.comment_id}

        if not risk_comment_ids:
            return 0.4

        # 计算这些评论的平均中心性
        risk_centralities = [
            graph_centrality.get(cid, 0.0) for cid in risk_comment_ids
        ]

        if not risk_centralities:
            return 0.4

        avg_centrality = np.mean(risk_centralities)

        # 归一化到 0-1
        return min(1.0, avg_centrality * 7)  # 假设中心性通常 < 0.2

    def _compute_burst_score(self, event: dict[str, Any]) -> float:
        """计算突增程度 (0-1)"""
        comments = event.get("comments", [])
        if len(comments) < 5:
            return 0.0

        # 简化版：评论数量越多，突增分越高
        # 实际应该基于时间窗口计算
        comment_count = len(comments)

        if comment_count < 10:
            return 0.4
        elif comment_count < 30:
            return 0.65
        elif comment_count < 50:
            return 0.8
        else:
            return 0.95

    def _compute_uncertainty_score(self, signals: list[RiskSignal]) -> float:
        """计算事实不确定性 (0-1)"""
        rumor_signals = [s for s in signals if s.signal_type == "rumor_spread"]

        if not rumor_signals:
            return 0.0

        # 传闻信号越多，不确定性越高
        return min(1.0, len(rumor_signals) * 0.3)

    def _map_score_to_level(self, score: float) -> RiskLevel:
        """映射分数到风险等级"""
        if score < 30:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _infer_evolution_stage(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
        resonance_score: float,
    ) -> tuple[EvolutionStage, list[EvolutionStage]]:
        """推断演化阶段"""
        comments = event.get("comments", [])

        # 阶段判断逻辑
        if len(comments) < 5 and any(s.signal_type == "negative_emotion" for s in signals):
            stage = EvolutionStage.COMPLAINT
            path = [EvolutionStage.COMPLAINT]

        elif any(s.signal_type == "rumor_spread" for s in signals):
            stage = EvolutionStage.VERIFICATION
            path = [EvolutionStage.COMPLAINT, EvolutionStage.VERIFICATION]

        elif resonance_score > 0.55:
            stage = EvolutionStage.RESONANCE
            path = [
                EvolutionStage.COMPLAINT,
                EvolutionStage.VERIFICATION,
                EvolutionStage.RESONANCE,
            ]

        elif any(s.signal_type == "confrontation" for s in signals):
            stage = EvolutionStage.POLARIZATION
            path = [
                EvolutionStage.COMPLAINT,
                EvolutionStage.RESONANCE,
                EvolutionStage.POLARIZATION,
            ]

        elif any(s.signal_type == "mobilization" for s in signals):
            stage = EvolutionStage.MOBILIZATION
            path = [
                EvolutionStage.COMPLAINT,
                EvolutionStage.RESONANCE,
                EvolutionStage.POLARIZATION,
                EvolutionStage.MOBILIZATION,
            ]

        else:
            stage = EvolutionStage.COMPLAINT
            path = [EvolutionStage.COMPLAINT]

        return stage, path

    def _identify_key_comments(
        self,
        event: dict[str, Any],
        signals: list[RiskSignal],
        graph_centrality: dict[str, float] | None,
    ) -> list[str]:
        """识别关键评论"""
        comments = event.get("comments", [])
        if not comments:
            return []

        # 为每条评论计算关键度
        comment_scores = []

        for comment in comments:
            comment_id = comment.get("comment_id", "")

            # 风险信号分数
            signal_score = sum(
                s.score for s in signals if s.comment_id == comment_id
            )

            # 图中心性分数
            centrality_score = (
                graph_centrality.get(comment_id, 0.0) if graph_centrality else 0.0
            )

            # 点赞分数
            like_score = np.log1p(comment.get("like_count", 0)) / 10

            # 综合分数
            total_score = (
                0.40 * signal_score + 0.35 * centrality_score * 5 + 0.25 * like_score
            )

            comment_scores.append((comment_id, total_score))

        # 排序并取 Top 3-5
        comment_scores.sort(key=lambda x: -x[1])
        top_k = min(5, max(3, len(comments) // 10))

        return [cid for cid, _ in comment_scores[:top_k]]

    def _compute_confidence(self, signals: list[RiskSignal]) -> float:
        """计算置信度"""
        if not signals:
            return 0.3

        # 信号数量越多，置信度越高
        signal_count_score = min(1.0, len(signals) / 10)

        # 信号分数越高，置信度越高
        avg_signal_score = np.mean([s.score for s in signals])

        confidence = 0.5 * signal_count_score + 0.5 * avg_signal_score

        return min(1.0, max(0.3, confidence))


if __name__ == "__main__":
    from backend.app.algorithms.risk_signals import RiskSignalDetector

    # 测试风险评分
    test_event = {
        "event_id": "E001",
        "post": {"text": "食堂价格太贵了，真是太过分了"},
        "comments": [
            {"comment_id": "C001", "text": "我也觉得太贵了，受不了", "like_count": 10},
            {"comment_id": "C002", "text": "听说要涨价了", "like_count": 5},
            {"comment_id": "C003", "text": "同感，我也是这样觉得", "like_count": 8},
            {"comment_id": "C004", "text": "今晚一起去食堂门口问清楚", "like_count": 15},
            {"comment_id": "C005", "text": "不解决就投诉", "like_count": 7},
        ],
    }

    # 检测信号
    detector = RiskSignalDetector()
    signals = detector.detect_signals(test_event, use_semantic=False)

    # 计算风险评分
    engine = RiskScoringEngine()
    assessment = engine.compute_risk_score(test_event, signals)

    print(f"风险评估结果:")
    print(f"  风险等级: {assessment.risk_level}")
    print(f"  风险分数: {assessment.risk_score:.2f}")
    print(f"  当前阶段: {assessment.current_stage}")
    print(f"  演化路径: {' -> '.join(assessment.evolution_path)}")
    print(f"  关键评论: {assessment.key_comments}")
    print(f"  置信度: {assessment.confidence:.2f}")
    print(f"  风险信号数: {len(assessment.risk_signals)}")
