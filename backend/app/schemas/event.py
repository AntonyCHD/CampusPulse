"""Event and Post schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .comment import Comment
from .enums import EventType


class Post(BaseModel):
    """主贴模型"""

    post_id: str
    source: str = "campus_wall"
    user_hash: Optional[str] = None
    title: Optional[str] = None
    text: str
    clean_text: Optional[str] = None
    created_at: datetime
    like_count: int = 0
    comment_count: int = 0
    image_paths: list[str] = Field(default_factory=list)


class CampusEvent(BaseModel):
    """校园事件模型"""

    event_id: str
    event_type: EventType
    post: Post
    comments: list[Comment]
    tags: list[str] = Field(default_factory=list)
    data_note: str = "授权获取并脱敏处理"
