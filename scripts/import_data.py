"""
完整的数据导入流程：转换 + 脱敏

使用方式:
    python scripts/import_data.py
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.anonymize_service import anonymize_jsonl_file
from backend.app.utils.data_transform import transform_jsonl_file


def import_and_process_data():
    """完整的数据导入和处理流程"""
    print("=" * 60)
    print("校园舆情数据导入流程")
    print("=" * 60)

    # 步骤 1: 数据转换
    print("\n[步骤 1/3] 数据格式转换...")
    raw_input = "data/raw/totalhot_articles_cleaned.jsonl"
    transformed_output = "data/processed/events_raw.jsonl"

    try:
        success, errors = transform_jsonl_file(raw_input, transformed_output)
        print(f"✓ 转换完成: 成功 {success} 条，失败 {errors} 条")
        print(f"  输出: {transformed_output}")
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return

    # 步骤 2: 数据脱敏
    print("\n[步骤 2/3] 数据脱敏处理...")
    anonymized_output = "data/processed/events.jsonl"

    try:
        count, stats = anonymize_jsonl_file(transformed_output, anonymized_output)
        print(f"✓ 脱敏完成: 处理 {count} 条事件")
        print(f"  - 用户ID映射: {stats['total_users']} 个")
        print(f"  - 用户昵称映射: {stats['total_names']} 个")
        print(f"  输出: {anonymized_output}")
    except Exception as e:
        print(f"✗ 脱敏失败: {e}")
        return

    # 步骤 3: 数据验证
    print("\n[步骤 3/3] 数据验证...")
    try:
        with open(anonymized_output, "r", encoding="utf-8") as f:
            events = [json.loads(line) for line in f]

        print(f"✓ 验证通过: {len(events)} 个事件")

        # 统计信息
        total_comments = sum(len(event.get("comments", [])) for event in events)
        event_types = {}
        for event in events:
            event_type = event.get("event_type", "未知")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print(f"\n数据统计:")
        print(f"  - 总事件数: {len(events)}")
        print(f"  - 总评论数: {total_comments}")
        print(f"  - 事件类型分布:")
        for event_type, count in sorted(event_types.items(), key=lambda x: -x[1]):
            print(f"    · {event_type}: {count}")

        # 显示第一个事件示例
        if events:
            print(f"\n示例事件 (ID: {events[0]['event_id']}):")
            print(f"  - 类型: {events[0]['event_type']}")
            print(f"  - 主贴文字: {events[0]['post']['text'][:50]}...")
            print(f"  - 评论数: {len(events[0]['comments'])}")

    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return

    print("\n" + "=" * 60)
    print("✓ 数据导入完成！")
    print("=" * 60)
    print(f"\n最终输出文件: {anonymized_output}")
    print("可以开始进行分析了。")


if __name__ == "__main__":
    import_and_process_data()