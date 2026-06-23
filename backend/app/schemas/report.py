"""Report schemas."""

from datetime import datetime

from pydantic import BaseModel

from .evidence import Evidence
from .risk import RiskAssessment


class InterventionAdvice(BaseModel):
    """处置建议"""

    summary: str
    official_statement: str
    action_items: list[str]
    avoid_phrases: list[str]
    responsible_department: list[str]
    urgency: str


class FinalReport(BaseModel):
    """最终报告"""

    event_id: str
    event_summary: str
    risk_assessment: RiskAssessment
    evidence: list[Evidence]
    intervention: InterventionAdvice
    generated_at: datetime
    mode: str  # realtime / cached
