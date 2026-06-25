"""Report schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

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


class KeyCommentExplanation(BaseModel):
    """关键评论解释"""

    comment_id: str
    reason: str
    risk_signal: str


class FinalReport(BaseModel):
    """最终报告"""

    event_id: str
    event_summary: str
    risk_assessment: RiskAssessment
    evidence: list[Evidence] = Field(default_factory=list)
    key_comment_explanations: list[KeyCommentExplanation] = Field(default_factory=list)
    intervention: InterventionAdvice
    human_review_required: bool = True
    generated_at: datetime
    mode: str  # realtime / cached
