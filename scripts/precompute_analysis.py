"""
预计算所有事件的分析结果并缓存
用于加速前端加载
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.analysis_service import get_analysis_service
from backend.app.storage.event_store import get_event_store


async def precompute_all_async():
    """预计算所有事件的分析结果"""
    print("开始预计算所有事件的分析结果...")

    store = get_event_store()
    service = get_analysis_service()

    events = store.get_all_events()
    total = len(events)

    print(f"找到 {total} 个事件")

    for i, event in enumerate(events, 1):
        event_id = event.get("event_id")
        print(f"\n[{i}/{total}] 分析事件 {event_id}...")

        try:
            # 先检查缓存
            cached = service._load_from_cache(event_id)
            if cached:
                print(f"  已有缓存，跳过")
                continue

            # 执行分析（会自动缓存）
            result = await service.analyze_event(event, mode="realtime")
            print(f"  完成: {result['risk_level']} (分数: {result['risk_score']:.2f})")

        except Exception as e:
            print(f"  [ERROR] 分析失败: {e}")
            continue

    print(f"\n预计算完成！共处理 {total} 个事件")


if __name__ == "__main__":
    asyncio.run(precompute_all_async())
