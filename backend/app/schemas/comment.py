"""Comment and CommentGraph schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import EmotionLabel, StanceLabel


class Comment(BaseModel):
    """评论模型"""

    comment_id: str
    parent_id: Optional[str] = None
    user_hash: Optional[str] = None
    text: str
    clean_text: Optional[str] = None
    created_at: datetime
    like_count: int = 0
    reply_count: int = 0
    emotion: Optional[EmotionLabel] = None
    stance: Optional[StanceLabel] = None
    risk_signals: list[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    """图节点"""

    node_id: str
    node_type: str  # post / comment
    label: str
    risk_score: float = 0.0
    size: int = 10
    group: Optional[str] = None


class GraphEdge(BaseModel):
    """图边"""

    source: str
    target: str
    edge_type: str  # reply / temporal / semantic
    weight: float = 1.0


class CommentGraph(BaseModel):
    """评论图谱"""

    event_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
