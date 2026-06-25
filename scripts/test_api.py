"""
测试脚本：验证完整分析流程
"""

import httpx
import json

API_BASE = "http://localhost:8000"

def test_complete_workflow():
    """测试完整工作流"""
    print("=" * 60)
    print("校园舆情监测系统 - 功能测试")
    print("=" * 60)

    with httpx.Client(timeout=120.0) as client:
        # 1. 获取事件列表
        print("\n[测试 1/4] 获取事件列表...")
        resp = client.get(f"{API_BASE}/api/events/")
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("items", [])
            print(f"[OK] 成功获取 {len(events)} 个事件")

            if events:
                test_event_id = events[0]["event_id"]
                print(f"  选择测试事件: {test_event_id}")
        else:
            print(f"[ERROR] 失败: {resp.status_code}")
            return

        # 2. 分析单个事件
        print(f"\n[测试 2/4] 分析事件 {test_event_id}...")
        resp = client.post(
            f"{API_BASE}/api/analyze/{test_event_id}",
            json={"mode": "cached", "use_llm": False}
        )

        if resp.status_code == 200:
            result = resp.json()
            print(f"[OK] 分析完成")
            print(f"  - 风险等级: {result.get('risk_level')}")
            print(f"  - 风险分数: {result.get('risk_score'):.2f}")
            print(f"  - 当前阶段: {result.get('current_stage')}")
            print(f"  - 风险信号: {len(result.get('risk_signals', []))} 个")
            print(f"  - 关键评论: {len(result.get('key_comments', []))} 条")
        else:
            print(f"[ERROR] 失败: {resp.status_code}")
            return

        # 3. 获取图谱数据
        print(f"\n[测试 3/4] 获取图谱数据...")
        resp = client.get(f"{API_BASE}/api/graph/{test_event_id}")

        if resp.status_code == 200:
            graph = resp.json()
            print(f"[OK] 图谱构建成功")
            print(f"  - 节点数: {len(graph.get('nodes', []))}")
            print(f"  - 边数: {len(graph.get('edges', []))}")

            # 统计边类型
            edges = graph.get('edges', [])
            edge_types = {}
            for edge in edges:
                edge_type = edge.get('edge_type', 'unknown')
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

            for edge_type, count in edge_types.items():
                print(f"    - {edge_type}: {count}")
        else:
            print(f"[ERROR] 失败: {resp.status_code}")
            return

        # 4. 基线方法对比
        print(f"\n[测试 4/4] 基线方法对比...")
        resp = client.post(
            f"{API_BASE}/api/baseline/{test_event_id}",
            params={"method": "all"}
        )

        if resp.status_code == 200:
            comparison = resp.json()
            print(f"[OK] 对比完成")

            # 评论链方法
            cc = comparison.get("comment_chain_method", {})
            print(f"\n  评论链演化法:")
            print(f"    风险等级: {cc.get('risk_level')}")
            print(f"    风险分数: {cc.get('risk_score'):.2f}")

            # 关键词法
            if "keyword_method" in comparison:
                kw = comparison["keyword_method"]
                print(f"\n  关键词法:")
                print(f"    风险等级: {kw.get('risk_level')}")
                print(f"    依据: {kw.get('reason')}")

            # 情感分析法
            if "sentiment_method" in comparison:
                sent = comparison["sentiment_method"]
                print(f"\n  情感分析法:")
                print(f"    风险等级: {sent.get('risk_level')}")
                print(f"    依据: {sent.get('reason')}")
        else:
            print(f"[ERROR] 失败: {resp.status_code}")
            return

    print("\n" + "=" * 60)
    print("[OK] 所有测试通过！系统运行正常。")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_complete_workflow()
    except httpx.ConnectError:
        print("[ERROR] 无法连接到后端服务")
        print("请先启动后端: uvicorn backend.app.main:app --reload")
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
