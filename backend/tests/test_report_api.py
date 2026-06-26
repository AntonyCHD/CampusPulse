"""Tests for report API evidence and structured output."""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import routes_report


class FakeStore:
    def get_event(self, event_id):
        return {
            "event_id": event_id,
            "event_type": "宿舍管理",
            "post": {"text": "宿舍断电影响复习", "created_at": "2026-06-25T10:00:00+08:00"},
            "comments": [
                {"comment_id": "C001", "text": "今晚一起去楼下问清楚", "like_count": 16},
                {"comment_id": "C002", "text": "有没有正式通知", "like_count": 5},
            ],
        }


class FakeAnalysisService:
    async def analyze_event(self, event, mode="cached", use_llm=False):
        return {
            "event_id": event["event_id"],
            "risk_level": "高",
            "risk_score": 76.0,
            "current_stage": "组织化行动",
            "evolution_path": ["个体吐槽", "信息求证", "组织化行动"],
            "confidence": 0.82,
            "key_comments": ["C001"],
            "risk_signals": [
                {
                    "signal_type": "mobilization",
                    "comment_id": "C001",
                    "evidence_text": "今晚一起去楼下问清楚",
                    "comment_text": "今晚一起去楼下问清楚",
                    "score": 0.9,
                    "reason": "包含行动号召且有时间或地点",
                    "source": "rule",
                }
            ],
            "mode": mode,
        }


def test_report_contains_evidence_and_key_comment_explanations(monkeypatch):
    monkeypatch.setattr(routes_report, "get_event_store", lambda: FakeStore())
    monkeypatch.setattr(routes_report, "get_analysis_service", lambda: FakeAnalysisService())

    client = TestClient(app)
    response = client.get("/api/report/E001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence"]
    assert payload["key_comment_explanations"]
    assert payload["key_comment_explanations"][0]["comment_id"] == "C001"
    assert isinstance(payload["human_review_required"], bool)
    assert payload["generated_at"]
    assert payload["intervention"]["action_items"]
