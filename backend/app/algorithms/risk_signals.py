"""
风险信号识别算法 v2

实现四层识别机制：
1. 规则兜底 - 关键词和模式匹配（含谐音/反讽/暗语检测）
2. 文本清洗增强 - 谐音还原、反讽模式识别
3. 语义识别 - 基于 embedding 的语义相似度
4. LLM 弱标注 - Top-N 评论的结构化标注

风险信号类型（8类）：
- negative_emotion: 明显负面情绪
- collective_resonance: 多人表达相同不满
- rumor_spread: 未证实传闻扩散
- sarcasm: 反讽/谐音/暗喻
- mobilization: 行动号召
- confrontation: 对抗倾向
- privacy_leak: 隐私泄露
- offline_risk: 线下聚集风险
"""

import re
from typing import Any

from backend.app.schemas.risk import RiskSignal
from backend.app.utils.text_cleaning import get_text_cleaner


class RiskSignalDetector:
    """风险信号检测器 v2"""

    def __init__(self):
        # --- Negative Emotion ---
        self.negative_keywords = [
            "愤怒", "生气", "气死", "恶心", "垃圾", "无语", "恼火",
            "受不了", "太过分", "不合理", "不公平", "太黑", "坑人",
            "骗人", "失望", "寒心", "心寒", "无奈", "烦躁", "崩溃",
        ]

        # --- Collective Resonance ---
        self.collective_keywords = [
            "我也是", "同感", "一样", "+1", "顶", "支持", "赞同",
            "大家", "我们", "都", "所有人", "一起", "我也",
        ]

        # --- Rumor Spread ---
        self.rumor_keywords = [
            "听说", "据说", "好像", "可能", "应该是", "传闻",
            "有人说", "朋友说", "同学说", "内部消息", "小道消息",
        ]

        # --- Sarcasm / Coded Language ---
        self.sarcasm_keywords = [
            "呵呵", "哈哈", "真是", "果然", "不愧", "厉害了",
        ]
        # Homophonic variants that indicate hidden meaning
        self.homophone_variants = {
            "垃圾": ["辣鸡", "LJ", "laji"],
            "傻逼": ["SB", "shabi", "傻B"],
            "无语": ["无雨", "wuyu"],
            "维权": ["维Q", "weiquan"],
            "举报": ["JB", "jubao"],
            "投诉": ["投su", "tousu"],
            "校领导": ["校LD", "校lingdao"],
            "教务处": ["教无处", "JW处"],
        }

        # --- Mobilization ---
        self.mobilization_keywords = [
            "一起", "集合", "组队", "大家去", "明天", "今晚",
            "报名", "参加", "行动", "投诉", "举报", "曝光",
            "联合", "组织", "约好",
        ]

        # --- Confrontation ---
        self.confrontation_keywords = [
            "闹", "搞", "不行就", "让他们", "不解决", "维权",
            "告", "找领导", "找校长", "举报", "曝光", "对峙",
        ]

        # Time and location patterns for offline risk
        self.time_pattern = re.compile(
            r"(今晚|明天|后天|周[一二三四五六日]|星期[一二三四五六日]|"
            r"\d+月\d+[日号]|\d+[点时]|\d+:\d+)"
        )
        self.location_pattern = re.compile(
            r"(楼[下上前后]?|门口|办公室|食堂|宿舍|操场|图书馆|"
            r"教学楼|行政楼|\d+号楼|\d+栋)"
        )

        # Phone / privacy patterns
        self.phone_pattern = re.compile(r"1[3-9]\d{9}")
        self.student_id_pattern = re.compile(r"\b\d{8,12}\b")
        self.dorm_pattern = re.compile(r"(宿舍|房间|寝室)\s*(号|编号)?\s*\d+")

        # Text cleaner for enhanced detection
        self.cleaner = get_text_cleaner()

    def detect_signals(
        self,
        event: dict[str, Any],
        use_semantic: bool = True,
    ) -> list[RiskSignal]:
        """
        Detect risk signals in an event

        Args:
            event: Event data with post and comments
            use_semantic: Whether to use semantic detection

        Returns:
            List of RiskSignal objects
        """
        signals: list[RiskSignal] = []

        # Detect signals in post text
        post = event.get("post", {})
        post_text = post.get("text", "")
        post_signals = self._detect_text_signals(post_text, comment_id=None, source="post")
        signals.extend(post_signals)

        # Detect signals in each comment
        comments = event.get("comments", [])
        for comment in comments:
            comment_text = comment.get("text", "")
            comment_id = comment.get("comment_id")
            comment_signals = self._detect_text_signals(comment_text, comment_id=comment_id, source="rule")
            signals.extend(comment_signals)

        # Collective resonance (across multiple comments)
        resonance_signals = self._detect_collective_resonance(comments)
        signals.extend(resonance_signals)

        # Semantic detection (placeholder for embedding-based)
        if use_semantic:
            semantic_signals = self._detect_semantic_signals(event)
            signals.extend(semantic_signals)

        return signals

    def _detect_text_signals(
        self,
        text: str,
        comment_id: str | None,
        source: str,
    ) -> list[RiskSignal]:
        """Enhanced rule-based text signal detection with homophone/sarcasm awareness"""
        signals: list[RiskSignal] = []

        if not text:
            return signals

        # Run text cleaning analysis for enhanced detection
        analysis = self.cleaner.full_analysis(text)

        # --- Negative Emotion ---
        neg_matches = [kw for kw in self.negative_keywords if kw in text]
        if neg_matches:
            signals.append(RiskSignal(
                signal_type="negative_emotion",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=min(0.95, 0.6 + len(neg_matches) * 0.08),
                reason=f"包含负面情绪词: {', '.join(neg_matches[:3])}",
                source=source,
            ))

        # --- Sarcasm / Homophone Detection (enhanced) ---
        sarcasm_hits = analysis.get("sarcasm", [])
        homophone_hits = analysis.get("homophones", [])

        if sarcasm_hits:
            sarcasm_types = [s["type"] for s in sarcasm_hits]
            signals.append(RiskSignal(
                signal_type="sarcasm",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=min(0.85, 0.55 + len(sarcasm_hits) * 0.1),
                reason=f"检测到反讽模式: {', '.join(sarcasm_types[:3])}",
                source="text_cleaner",
            ))

        if homophone_hits:
            corrected = [f"{h['matched']}->{h['corrected_to']}" for h in homophone_hits]
            signals.append(RiskSignal(
                signal_type="sarcasm",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=min(0.8, 0.6 + len(homophone_hits) * 0.05),
                reason=f"检测到谐音/暗语: {', '.join(corrected[:3])}",
                source="text_cleaner",
            ))

        # Fallback: simple keyword-based sarcasm detection
        if not sarcasm_hits and not homophone_hits:
            if any(kw in text for kw in self.sarcasm_keywords):
                if "真是" in text or "不愧" in text or "厉害了" in text:
                    signals.append(RiskSignal(
                        signal_type="sarcasm",
                        comment_id=comment_id,
                        evidence_text=text[:80],
                        score=0.5,
                        reason="可能包含反讽表达（关键词匹配）",
                        source=source,
                    ))

        # --- Rumor Spread ---
        rumor_matches = [kw for kw in self.rumor_keywords if kw in text]
        if rumor_matches:
            signals.append(RiskSignal(
                signal_type="rumor_spread",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=min(0.9, 0.6 + len(rumor_matches) * 0.08),
                reason=f"包含传闻扩散表达: {', '.join(rumor_matches[:3])}",
                source=source,
            ))

        # --- Mobilization ---
        mob_matches = [kw for kw in self.mobilization_keywords if kw in text]
        if mob_matches:
            has_time = bool(self.time_pattern.search(text))
            has_location = bool(self.location_pattern.search(text))

            if has_time and has_location:
                score = 0.9
                reason = "包含行动号召且有明确时间地点"
            elif has_time or has_location:
                score = 0.8
                reason = "包含行动号召且有时间或地点信息"
            else:
                score = 0.75
                reason = f"包含行动号召表达: {', '.join(mob_matches[:3])}"

            signals.append(RiskSignal(
                signal_type="mobilization",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=score,
                reason=reason,
                source=source,
            ))

        # --- Confrontation ---
        conf_matches = [kw for kw in self.confrontation_keywords if kw in text]
        if conf_matches:
            signals.append(RiskSignal(
                signal_type="confrontation",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=min(0.9, 0.6 + len(conf_matches) * 0.08),
                reason=f"包含对抗倾向: {', '.join(conf_matches[:3])}",
                source=source,
            ))

        # --- Privacy Leak ---
        privacy_hits = analysis.get("privacy", [])
        if privacy_hits:
            leak_types = [p["type"] for p in privacy_hits]
            signals.append(RiskSignal(
                signal_type="privacy_leak",
                comment_id=comment_id,
                evidence_text="[已隐藏]",
                score=0.9,
                reason=f"包含敏感信息: {', '.join(leak_types)}",
                source="text_cleaner",
            ))

        # --- Offline Risk ---
        has_time = bool(self.time_pattern.search(text))
        has_location = bool(self.location_pattern.search(text))
        has_mobilization = bool(mob_matches)

        if has_time and has_location and (has_mobilization or "去" in text or "到" in text):
            signals.append(RiskSignal(
                signal_type="offline_risk",
                comment_id=comment_id,
                evidence_text=text[:80],
                score=0.9,
                reason="检测到时间+地点+行动意图，存在线下聚集风险",
                source=source,
            ))

        return signals

    def _detect_collective_resonance(
        self,
        comments: list[dict[str, Any]],
    ) -> list[RiskSignal]:
        """Detect collective resonance across multiple comments"""
        signals: list[RiskSignal] = []

        resonance_count = 0
        resonance_comment_ids: list[str] = []

        for comment in comments:
            text = comment.get("text", "")
            if any(kw in text for kw in self.collective_keywords):
                resonance_count += 1
                cid = comment.get("comment_id")
                if cid:
                    resonance_comment_ids.append(cid)

        threshold = max(2, len(comments) * 0.2)
        if resonance_count >= threshold:
            signals.append(RiskSignal(
                signal_type="collective_resonance",
                comment_id=None,
                evidence_text=f"{resonance_count}条评论表达共鸣",
                score=min(0.9, 0.5 + resonance_count * 0.05),
                reason=f"多人({resonance_count}人)表达相同不满或共鸣",
                source="collective",
            ))

        return signals

    def _detect_semantic_signals(
        self,
        event: dict[str, Any],
    ) -> list[RiskSignal]:
        """Semantic-based signal detection (placeholder)"""
        # TODO: Implement embedding-based cluster detection
        return []


if __name__ == "__main__":
    detector = RiskSignalDetector()

    test_texts = [
        "食堂价格太贵了，辣鸡学校",
        "我也是，真的受不了",
        "听说要涨价了，内部消息",
        "今晚一起去食堂门口问清楚",
        "学校真是太贴心了，呵呵",
        "教无处的人真是SB",
        "我是SB 不是那个意思",
    ]

    for text in test_texts:
        print(f"\n--- {text}")
        signals = detector._detect_text_signals(text, comment_id=None, source="test")
        for s in signals:
            print(f"  [{s.signal_type}] score={s.score:.2f} reason={s.reason}")