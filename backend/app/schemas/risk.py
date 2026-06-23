"""Risk assessment schemas."""

from typing import Optional

from pydantic import BaseModel

from .enums import EvolutionStage, RiskLevel


class RiskSignal(BaseModel):
    """风险信号"""

    signal_type: str
    comment_id: Optional[str] = None
    evidence_text: str
    score: float
    reason: str
    source: str = "rule"  # rule / semantic / llm


class RiskAssessment(BaseModel):
    """风险评估结果"""

    event_id: str
    risk_level: RiskLevel
    risk_score: float
    current_stage: EvolutionStage
    evolution_path: list[EvolutionStage]
    key_comments: list[str]
    risk_signals: list[RiskSignal]
    confidence: float
