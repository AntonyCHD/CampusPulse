"""Tests for event listing summary API."""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api import routes_events


class FakeStore:
    def get_all_events(self, risk_level=None, event_type=None, limit=100):
        events = [
            {
                "event_id": "E001",
                "event_type": "宿舍管理",
                "post": {"text": "宿舍断电", "like_count": 10, "created_at": "2026-06-25T10:00:00+08:00"},
                "comments": [{"comment_id": "C001"}],
            },
            {
                "event_id": "E002",
                "event_type": "食堂餐饮",
                "post": {"text": "食堂价格", "like_count": 3, "created_at": "2026-06-24T10:00:00+08:00"},
                "comments": [],
            },
        ]
        if event_type:
            events = [event for event in events if event["event_type"] == event_type]
        return events[:limit]


class FakeAnalysisService:
    def _load_from_cache(self, event_id):
        return {
            "E001": {"risk_level": "高", "risk_score": 72.5},
            "E002": {"risk_level": "低", "risk_score": 18.0},
        }.get(event_id)


def test_events_response_contains_dashboard_summary(monkeypatch):
    monkeypatch.setattr(routes_events, "get_event_store", lambda: FakeStore())

    import backend.app.services.analysis_service as analysis_module

    monkeypatch.setattr(analysis_module, "get_analysis_service", lambda: FakeAnalysisService())

    client = TestClient(app)
    response = client.get("/api/events/")

    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert payload["summary"]["total_events"] == 2
    assert payload["summary"]["high_risk_events"] == 1
    assert payload["summary"]["risk_distribution"]["高"] == 1
    assert payload["summary"]["event_type_distribution"]["宿舍管理"] == 1
    assert payload["summary"]["risk_trend"]
