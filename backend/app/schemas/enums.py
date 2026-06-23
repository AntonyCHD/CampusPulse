"""Enumeration types for the system."""

from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""

    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "严重"


class EventType(str, Enum):
    """事件类型"""

    LOGISTICS = "后勤服务"
    TEACHING = "教学教务"
    DORMITORY = "宿舍管理"
    CANTEEN = "食堂餐饮"
    SAFETY = "校园安全"
    ADMIN = "管理制度"
    RUMOR = "传闻求证"
    OTHER = "其他"


class EvolutionStage(str, Enum):
    """演化阶段"""

    COMPLAINT = "个体吐槽"
    VERIFICATION = "信息求证"
    RESONANCE = "情绪共振"
    POLARIZATION = "立场对立"
    MOBILIZATION = "组织化行动"
    OFFLINE_RISK = "线下风险"


class StanceLabel(str, Enum):
    """立场标签"""

    SUPPORT = "支持"
    OPPOSE = "反对"
    QUESTION = "求证"
    MOCK = "调侃反讽"
    SUGGEST = "建议"
    RUMOR_REFUTE = "辟谣"
    MOBILIZE = "号召"
    ATTACK = "攻击"


class EmotionLabel(str, Enum):
    """情绪标签"""

    NEUTRAL = "中性"
    ANGER = "愤怒"
    ANXIETY = "焦虑"
    DISAPPOINTMENT = "失望"
    SATIRE = "讽刺"
    FEAR = "恐慌"
    TRUST = "信任"
