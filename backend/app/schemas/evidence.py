"""Evidence schemas."""

from pydantic import BaseModel


class Evidence(BaseModel):
    """证据模型"""

    evidence_id: str
    title: str
    source: str
    content: str
    score: float
    evidence_type: str  # policy / notice / history_case / response_template
