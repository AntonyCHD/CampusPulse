"""示例数据生成脚本"""

import json
from datetime import datetime, timedelta


def generate_demo_event():
    """生成演示用的事件数据"""
    event = {
        "event_id": "E001",
        "event_type": "宿舍管理",
        "post": {
            "post_id": "P001",
            "source": "campus_wall",
            "user_hash": "U_a1b2c3",
            "title": None,
            "text": "宿舍12点后就断电了，严重影响复习，希望学校能重新考虑这个政策",
            "clean_text": "宿舍12点后就断电了，严重影响复习，希望学校能重新考虑这个政策",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "like_count": 45,
            "comment_count": 8,
            "image_paths": [],
        },
        "comments": [
            {
                "comment_id": "C001",
                "parent_id": None,
                "user_hash": "U_d4e5f6",
                "text": "同感，现在期末复习时间根本不够",
                "clean_text": "同感，现在期末复习时间根本不够",
                "created_at": (datetime.now() - timedelta(hours=1, minutes=50)).isoformat(),
                "like_count": 32,
                "reply_count": 0,
            },
            {
                "comment_id": "C002",
                "parent_id": None,
                "user_hash": "U_g7h8i9",
                "text": "有没有通知为什么突然限电？",
                "clean_text": "有没有通知为什么突然限电？",
                "created_at": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
                "like_count": 28,
                "reply_count": 1,
            },
            {
                "comment_id": "C003",
                "parent_id": "C002",
                "user_hash": "U_j1k2l3",
                "text": "听说是为了节能，但没看到正式通知",
                "clean_text": "听说是为了节能，但没看到正式通知",
                "created_at": (datetime.now() - timedelta(hours=1, minutes=40)).isoformat(),
                "like_count": 15,
                "reply_count": 0,
            },
            {
                "comment_id": "C004",
                "parent_id": None,
                "user_hash": "U_m4n5o6",
                "text": "这个政策真的不合理，影响太大了",
                "clean_text": "这个政策真的不合理，影响太大了",
                "created_at": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                "like_count": 38,
                "reply_count": 0,
            },
        ],
        "tags": ["宿舍", "限电", "复习"],
        "data_note": "授权获取并脱敏处理",
    }
    return event


if __name__ == "__main__":
    event = generate_demo_event()

    # 保存到 demo_cases
    output_path = "data/demo_cases/E001.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(event, f, ensure_ascii=False, indent=2)

    print(f"演示事件已生成: {output_path}")
