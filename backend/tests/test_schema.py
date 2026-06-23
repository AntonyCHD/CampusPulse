"""Test Pydantic schemas."""

from datetime import datetime

from backend.app.schemas import CampusEvent, Comment, Post
from backend.app.schemas.enums import EventType, RiskLevel


def test_post_schema():
    """Test Post schema"""
    post = Post(
        post_id="P001",
        text="测试主贴",
        clean_text="测试主贴",
        created_at=datetime.now(),
        like_count=10,
    )
    assert post.post_id == "P001"
    assert post.like_count == 10


def test_comment_schema():
    """Test Comment schema"""
    comment = Comment(
        comment_id="C001",
        text="测试评论",
        clean_text="测试评论",
        created_at=datetime.now(),
        like_count=5,
    )
    assert comment.comment_id == "C001"
    assert comment.like_count == 5


def test_campus_event_schema():
    """Test CampusEvent schema"""
    post = Post(
        post_id="P001",
        text="测试主贴",
        created_at=datetime.now(),
    )

    comment = Comment(
        comment_id="C001",
        text="测试评论",
        created_at=datetime.now(),
    )

    event = CampusEvent(
        event_id="E001",
        event_type=EventType.DORMITORY,
        post=post,
        comments=[comment],
    )

    assert event.event_id == "E001"
    assert event.event_type == EventType.DORMITORY
    assert len(event.comments) == 1
