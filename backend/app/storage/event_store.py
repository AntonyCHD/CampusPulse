"""
数据存储服务

简单的内存/文件存储，用于 MVP 阶段
"""

import json
from pathlib import Path
from typing import Any


class EventStore:
    """事件存储"""

    def __init__(self, data_path: str = "data/processed/events.jsonl"):
        """
        初始化存储

        Args:
            data_path: 数据文件路径
        """
        self.data_path = Path(data_path)
        self._events: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def _load_events(self):
        """加载所有事件到内存"""
        if self._loaded:
            return

        if not self.data_path.exists():
            print(f"警告: 数据文件不存在 {self.data_path}")
            self._loaded = True
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    event_id = event.get("event_id")
                    if event_id:
                        self._events[event_id] = event
                except Exception as e:
                    print(f"加载事件失败: {e}")

        self._loaded = True
        print(f"[OK] 加载了 {len(self._events)} 个事件")

    def get_all_events(
        self,
        risk_level: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        获取所有事件

        Args:
            risk_level: 风险等级过滤
            event_type: 事件类型过滤
            limit: 返回数量限制

        Returns:
            事件列表
        """
        self._load_events()

        events = list(self._events.values())

        # 过滤
        if risk_level:
            # 暂时返回全部，实际需要根据分析结果过滤
            pass

        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]

        # 限制数量
        events = events[:limit]

        return events

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """
        获取单个事件

        Args:
            event_id: 事件ID

        Returns:
            事件数据，不存在返回 None
        """
        self._load_events()
        return self._events.get(event_id)

    def get_event_count(self) -> int:
        """获取事件总数"""
        self._load_events()
        return len(self._events)


# 全局单例
_event_store: EventStore | None = None


def get_event_store() -> EventStore:
    """获取事件存储单例"""
    global _event_store
    if _event_store is None:
        _event_store = EventStore()
    return _event_store
