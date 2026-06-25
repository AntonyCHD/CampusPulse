"""
基线方法服务

实现简单的基线方法用于对比：
1. 关键词法 - 基于负面关键词计数
2. 情感分析法 - 基于情感词典
"""

from typing import Any


class BaselineService:
    """基线方法服务"""

    def __init__(self):
        """初始化基线服务"""
        # 负面关键词
        self.negative_keywords = [
            "愤怒", "生气", "垃圾", "恶心", "无语", "受不了", "太过分",
            "不合理", "不公平", "失望", "寒心", "抗议", "投诉"
        ]

        # 中性关键词
        self.neutral_keywords = ["希望", "建议", "请问", "能否", "是否"]

    def keyword_method(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        关键词法

        只看关键词匹配，不考虑语义和结构
        """
        post_text = event.get("post", {}).get("text", "")
        comments = event.get("comments", [])

        # 统计负面关键词
        negative_count = 0
        for keyword in self.negative_keywords:
            if keyword in post_text:
                negative_count += 1

            for comment in comments:
                if keyword in comment.get("text", ""):
                    negative_count += 1

        # 简单映射到风险等级
        total_texts = 1 + len(comments)
        negative_ratio = negative_count / max(1, total_texts)

        if negative_ratio >= 0.5:
            risk_level = "高"
        elif negative_ratio >= 0.3:
            risk_level = "中"
        else:
            risk_level = "低"

        return {
            "method": "关键词法",
            "risk_level": risk_level,
            "reason": f"检测到{negative_count}个负面关键词，占比{negative_ratio:.1%}",
            "details": {
                "negative_count": negative_count,
                "total_texts": total_texts,
                "negative_ratio": negative_ratio,
            },
        }

    def sentiment_method(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        情感分析法

        基于简单的情感词典，不考虑上下文
        """
        post_text = event.get("post", {}).get("text", "")
        comments = event.get("comments", [])

        # 统计情感
        negative_count = 0
        neutral_count = 0

        # 主贴
        for keyword in self.negative_keywords:
            if keyword in post_text:
                negative_count += 1

        for keyword in self.neutral_keywords:
            if keyword in post_text:
                neutral_count += 1

        # 评论
        for comment in comments:
            text = comment.get("text", "")
            for keyword in self.negative_keywords:
                if keyword in text:
                    negative_count += 1

            for keyword in self.neutral_keywords:
                if keyword in text:
                    neutral_count += 1

        # 计算情感占比
        total = negative_count + neutral_count + 1
        negative_ratio = negative_count / total

        if negative_ratio >= 0.6:
            risk_level = "高"
        elif negative_ratio >= 0.4:
            risk_level = "中"
        else:
            risk_level = "低"

        return {
            "method": "情感分析法",
            "risk_level": risk_level,
            "reason": f"负面情感占比{negative_ratio:.1%}",
            "details": {
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "negative_ratio": negative_ratio,
            },
        }


# 全局单例
_baseline_service: BaselineService | None = None


def get_baseline_service() -> BaselineService:
    """获取基线服务单例"""
    global _baseline_service
    if _baseline_service is None:
        _baseline_service = BaselineService()
    return _baseline_service
