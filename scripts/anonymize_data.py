"""脱敏工具脚本"""

import re
import hashlib


def anonymize_text(text: str) -> str:
    """对文本进行脱敏处理"""
    # 替换手机号
    text = re.sub(r"1[3-9]\d{9}", "[电话]", text)

    # 替换学号（假设为8-10位数字）
    text = re.sub(r"\b\d{8,10}\b", "[学号]", text)

    # 替换宿舍号（格式如：1-101、A栋301等）
    text = re.sub(r"[A-Z]?\d{1,2}[-栋]\d{3,4}", "[宿舍号]", text)
    text = re.sub(r"[A-Z栋]?\d{3,4}室", "[宿舍号]", text)

    # 替换邮箱
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[邮箱]", text)

    return text


def hash_user_id(user_id: str, salt: str = "default_salt") -> str:
    """将用户ID哈希化"""
    combined = f"{user_id}{salt}"
    hash_obj = hashlib.md5(combined.encode())
    return f"U_{hash_obj.hexdigest()[:6]}"


if __name__ == "__main__":
    # 测试
    test_text = "我是13800138000，学号20210001，住在A栋301室"
    print("原文:", test_text)
    print("脱敏后:", anonymize_text(test_text))

    test_user = "user_12345"
    print("用户ID:", test_user)
    print("哈希后:", hash_user_id(test_user))
