"""Tests for hard-coded evidence retrieval."""


def test_retrieve_returns_ranked_evidence_for_dormitory_event():
    from backend.app.services.rag_service import RagService

    service = RagService()
    event = {
        "event_id": "E001",
        "event_type": "宿舍管理",
        "post": {"text": "宿舍晚上断电影响复习，想知道后勤有没有通知"},
        "comments": [
            {"comment_id": "C001", "text": "今晚一起去楼下问清楚", "like_count": 12},
            {"comment_id": "C002", "text": "有没有正式通知", "like_count": 4},
        ],
    }

    evidence = service.retrieve(event, top_k=3)

    assert evidence
    assert len(evidence) <= 3
    assert evidence[0].score >= evidence[-1].score
    assert any(item.evidence_type in {"policy", "notice", "response_template"} for item in evidence)
    assert any("宿舍" in item.title or "后勤" in item.content for item in evidence)


def test_retrieve_returns_general_fallback_when_no_keyword_matches():
    from backend.app.services.rag_service import RagService

    service = RagService()
    event = {
        "event_id": "E002",
        "event_type": "其他",
        "post": {"text": "普通校园日常讨论"},
        "comments": [],
    }

    evidence = service.retrieve(event, top_k=2)

    assert evidence
    assert len(evidence) <= 2
    assert all(item.source for item in evidence)
