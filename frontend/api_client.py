"""API client for frontend."""

import httpx


class APIClient:
    """API client for Campus Opinion Radar."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def get_events(self, risk_level: str | None = None, limit: int = 20):
        """获取事件列表"""
        params = {"limit": limit}
        if risk_level:
            params["risk_level"] = risk_level

        response = await self.client.get("/api/events/", params=params)
        response.raise_for_status()
        return response.json()

    async def get_event(self, event_id: str):
        """获取单个事件"""
        response = await self.client.get(f"/api/events/{event_id}")
        response.raise_for_status()
        return response.json()

    async def analyze_event(
        self,
        event_id: str,
        mode: str = "realtime",
        use_llm: bool = True,
        use_rag: bool = True,
    ):
        """分析事件"""
        payload = {
            "mode": mode,
            "use_llm": use_llm,
            "use_rag": use_rag,
        }
        response = await self.client.post(f"/api/analyze/{event_id}", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_graph(self, event_id: str):
        """获取评论图谱"""
        response = await self.client.get(f"/api/graph/{event_id}")
        response.raise_for_status()
        return response.json()

    async def get_report(self, event_id: str):
        """获取报告"""
        response = await self.client.get(f"/api/report/{event_id}")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close client"""
        await self.client.aclose()
