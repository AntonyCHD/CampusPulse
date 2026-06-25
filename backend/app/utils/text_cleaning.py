"""
Text Cleaning & Preprocessing Utility

Handles:
- Content-based cleaning for Chinese social media text
- Homophonic character detection (谐音字检测)
- Sarcasm pattern detection (反讽模式)
- Coded language recognition (暗语/密码式表达)
- URL, emoji, special character normalization
"""

import re
from typing import Any


class TextCleaner:
    """Chinese social media text cleaner with homophonic/sarcasm awareness"""

    # Common homophonic substitutions in Chinese campus forums
    HOMOPHONE_MAP = {
        # Administrative terms
        "校领导": ["校灵道", "校LD", "校lingdao", "领导们"],
        "辅导员": ["辅倒员", "F导员", "fudaoyuan"],
        "教务处": ["教无处", "JW处", "jiaowuchu"],
        "学生处": ["学S处", "XS处"],
        # Sensitive terms
        "举报": ["JB", "jubao", "举鲍"],
        "投诉": ["投su", "tousu", "TS"],
        "上访": ["上F", "shangfang"],
        "维权": ["维Q", "weiquan"],
        # Campus-related
        "食堂": ["食唐", "shitang", "ST"],
        "宿舍": ["宿社", "sushe", "SS"],
        "停电": ["停dian", "tingdian"],
        "涨价": ["涨J", "zhangjia"],
        # Emotion-related
        "无语": ["无雨", "wuyu"],
        "恶心": ["恶❤", "exin"],
        "垃圾": ["辣鸡", "LJ", "laji"],
        "坑人": ["坑R", "kengren"],
        "傻逼": ["SB", "shabi", "傻B"],
        # Action-related  
        "集合": ["jihe", "JH", "集和"],
        "组队": ["zudui", "ZD"],
        "曝光": ["BG", "baoguang", "暴光"],
    }

    # Sarcasm patterns
    SARCASM_PATTERNS = [
        # "真是太贴心了" type
        (r"真是\s*太?\s*(贴心|周到|负责|认真|感动|温暖|人性化)", "sarcasm_praise"),
        # "感谢学校" type
        (r"(感谢|谢谢|感恩)\s*(学校|领导|老师|食堂|后勤)", "sarcasm_thanks"),
        # "不愧是世界一流大学"
        (r"不愧\s*是", "sarcasm_不愧"),
        # "厉害了"
        (r"厉害\s*了", "sarcasm_厉害了"),
        # "666" used ironically
        (r"\b6{2,}\b", "sarcasm_666"),
        # "呵呵"
        (r"呵\s*呵", "sarcasm_呵呵"),
        # "果然"
        (r"果\s*然", "sarcasm_果然"),
        # Rhetorical questions indicating sarcasm
        (r"(难道|莫非)\s*(只有|就)\s*我.*[？?]", "sarcasm_rhetorical"),
    ]

    # Coded/abbreviated expression patterns
    CODED_PATTERNS = [
        # Pinyin initials: "jwc" -> 教务处
        (r"\b([a-z]{2,4})\b", "pinyin_abbr"),
        # Number codes: "520" type
        (r"\b\d{3,6}\b", "number_code"),
        # Asterisk substitution: "傻*"
        (r"[*\u2605\u2606\u2731]", "asterisk_mask"),
    ]

    # Privacy leak patterns
    PRIVACY_PATTERNS = [
        (r"1[3-9]\d{9}", "phone"),
        (r"\b\d{8,12}\b", "student_id"),  # Student ID
        (r"(宿舍|房间|寝室)\s*(号|编号)?\s*\d+", "dorm_number"),
        (r"\d{6}\s*(室|房间)", "dorm_number"),
        (r"([\u4e00-\u9fa5]{2,4})\s*(老师|教授|辅导员|主任|校长)", "real_name"),
    ]

    def __init__(self):
        # Build reverse lookup for homophone detection
        self.homophone_reverse: dict[str, str] = {}
        for correct, variants in self.HOMOPHONE_MAP.items():
            for v in variants:
                self.homophone_reverse[v.lower()] = correct

        # Compile regex patterns
        self._sarcasm_re = [(re.compile(p, re.IGNORECASE), t) for p, t in self.SARCASM_PATTERNS]
        self._coded_re = [(re.compile(p, re.IGNORECASE), t) for p, t in self.CODED_PATTERNS]
        self._privacy_re = [(re.compile(p), t) for p, t in self.PRIVACY_PATTERNS]

    def clean_text(self, text: str) -> str:
        """
        Basic text cleaning: remove excessive whitespace, normalize punctuation
        """
        if not text:
            return ""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Normalize repeated punctuation
        text = re.sub(r"([!?！？。，,.])\1{2,}", r"\1\1", text)
        # Remove control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        return text

    def detect_homophones(self, text: str) -> list[dict[str, Any]]:
        """
        Detect homophonic substitutions in text

        Returns:
            List of {original: str, substitution: str, corrected: str}
        """
        results = []
        text_lower = text.lower()

        for variant, correct in self.homophone_reverse.items():
            if variant in text_lower:
                results.append({
                    "original": text,
                    "matched": variant,
                    "corrected_to": correct,
                    "type": "homophone",
                })

        return results

    def detect_sarcasm(self, text: str) -> list[dict[str, Any]]:
        """Detect sarcasm patterns in text"""
        results = []
        for pattern, sarcasm_type in self._sarcasm_re:
            match = pattern.search(text)
            if match:
                results.append({
                    "text": text,
                    "matched": match.group(),
                    "type": sarcasm_type,
                    "confidence": 0.7 if sarcasm_type in ("sarcasm_呵呵", "sarcasm_666") else 0.6,
                })
        return results

    def detect_coded_expressions(self, text: str) -> list[dict[str, Any]]:
        """Detect coded/abbreviated expressions"""
        results = []
        for pattern, code_type in self._coded_re:
            matches = pattern.findall(text)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0]
                if len(m) >= 2:  # Skip single characters
                    results.append({
                        "text": text,
                        "matched": m,
                        "type": code_type,
                    })
        return results

    def detect_privacy_leaks(self, text: str) -> list[dict[str, Any]]:
        """Detect potential privacy leaks in text"""
        results = []
        for pattern, leak_type in self._privacy_re:
            match = pattern.search(text)
            if match:
                results.append({
                    "text": "[REDACTED]",
                    "matched": match.group(),
                    "type": leak_type,
                })
        return results

    def full_analysis(self, text: str) -> dict[str, Any]:
        """
        Complete text analysis: cleaning + all detection
        """
        if not text:
            return {"clean_text": "", "homophones": [], "sarcasm": [], "coded": [], "privacy": []}

        return {
            "clean_text": self.clean_text(text),
            "homophones": self.detect_homophones(text),
            "sarcasm": self.detect_sarcasm(text),
            "coded": self.detect_coded_expressions(text),
            "privacy": self.detect_privacy_leaks(text),
        }

    def analyze_batch(self, texts: list[str]) -> list[dict[str, Any]]:
        """Analyze multiple texts"""
        return [self.full_analysis(t) for t in texts]


# Singleton
_text_cleaner: TextCleaner | None = None


def get_text_cleaner() -> TextCleaner:
    global _text_cleaner
    if _text_cleaner is None:
        _text_cleaner = TextCleaner()
    return _text_cleaner