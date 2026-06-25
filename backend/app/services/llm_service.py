"""
LLM Service - OpenAI-compatible API client with caching

Supports: OpenAI, DeepSeek, Qwen (Tongyi), Zhipu (GLM), custom providers
Per design doc M8: LLM is "structured annotator" and "report generator"
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """OpenAI-compatible LLM API client with response caching"""

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        model: str | None = None,
        cache_dir: str = "./cache/llm_responses",
        cache_ttl_hours: int = 24,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.api_base = (api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key not in ("your_openai_api_key_here", ""))

    def _cache_key(self, messages: list[dict], **kwargs) -> str:
        """Generate a cache key from messages and parameters"""
        import hashlib
        content = json.dumps({"messages": messages, "model": self.model, **kwargs}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _load_cache(self, cache_key: str) -> dict | None:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01T00:00:00"))
            if datetime.now() - cached_at > self.cache_ttl:
                return None
            return data.get("response")
        except Exception:
            return None

    def _save_cache(self, cache_key: str, response: dict):
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "cached_at": datetime.now().isoformat(),
                    "model": self.model,
                    "cache_key": cache_key,
                    "response": response,
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save LLM cache: {e}")

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: dict | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Send chat completion request to LLM provider

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            response_format: Optional {"type": "json_object"} for structured output
            use_cache: Whether to use response caching

        Returns:
            API response dict with choices, usage, etc.
        """
        if not self.is_configured:
            raise ValueError("LLM API key not configured. Set OPENAI_API_KEY in .env")

        cache_key = self._cache_key(messages, temperature=temperature, max_tokens=max_tokens)
        if use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                logger.info(f"LLM cache hit: {cache_key}")
                return cached

        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            body["response_format"] = response_format

        client = await self._get_client()
        url = f"{self.api_base}/chat/completions"

        logger.info(f"LLM request: model={self.model}, msgs={len(messages)}, temp={temperature}")
        start = time.time()

        try:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            result = resp.json()
            elapsed = time.time() - start
            usage = result.get("usage", {})
            logger.info(
                f"LLM response: {elapsed:.1f}s, "
                f"tokens: in={usage.get('prompt_tokens', '?')} out={usage.get('completion_tokens', '?')}"
            )

            if use_cache:
                self._save_cache(cache_key, result)

            return result

        except httpx.HTTPStatusError as e:
            error_body = ""
            try:
                error_body = e.response.text[:500]
            except Exception:
                pass
            logger.error(f"LLM HTTP error {e.response.status_code}: {error_body}")
            raise RuntimeError(f"LLM API error ({e.response.status_code}): {error_body}") from e
        except httpx.RequestError as e:
            logger.error(f"LLM request error: {e}")
            raise RuntimeError(f"LLM connection error: {e}") from e

    async def structured_analysis(
        self,
        context: dict[str, Any],
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        M8: Structured risk analysis - sends assessment context to LLM

        Args:
            context: Structured assessment context per design doc M8
                - event_summary
                - risk_score, risk_level, current_stage
                - risk_signals: [{type, comment_id, text}]
                - key_comments: [comment_ids]
                - evidence: [{title, content}]
                - baseline_result

        Returns:
            Parsed JSON dict with:
                - risk_reason, evolution_explanation
                - key_comment_explanations
                - intervention: {official_statement, action_items, avoid_phrases, responsible_department, urgency}
                - human_review_required
        """
        import json as json_mod

        system_prompt = """你是校园舆情风险分析师。你需要基于提供的结构化分析数据，生成：
1. 风险原因分析
2. 演化路径解释
3. 关键评论说明
4. 温和处置建议

请严格按照 JSON Schema 输出，不要包含额外文字。"""

        user_prompt = f"""分析以下校园舆情事件：

事件摘要：{context.get('event_summary', 'N/A')}
风险评分：{context.get('risk_score', 0):.1f}
风险等级：{context.get('risk_level', 'N/A')}
当前阶段：{context.get('current_stage', 'N/A')}

识别到的风险信号：
{json_mod.dumps(context.get('risk_signals', []), ensure_ascii=False, indent=2)}

关键评论ID：{json_mod.dumps(context.get('key_comments', []), ensure_ascii=False)}

相关证据：
{json_mod.dumps(context.get('evidence', []), ensure_ascii=False, indent=2)}

基线对比结果：
{json_mod.dumps(context.get('baseline_result', {}), ensure_ascii=False, indent=2)}

请输出以下 JSON（不要包含 markdown 代码块标记）：
{{
  "risk_reason": "详细的风险原因分析（2-3句话）",
  "evolution_explanation": ["阶段1解释", "阶段2解释"],
  "key_comment_explanations": [
    {{"comment_id": "C001", "reason": "为什么这条评论关键", "risk_signal": "信号类型"}}
  ],
  "intervention": {{
    "official_statement": "建议的官方回应话术",
    "action_items": ["行动项1", "行动项2"],
    "avoid_phrases": ["避免使用的话术1"],
    "responsible_department": ["责任部门"],
    "urgency": "处置时限（如：24小时内）"
  }},
  "human_review_required": true
}}"""

        try:
            result = await self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=4096,
                response_format={"type": "json_object"},
                use_cache=use_cache,
            )

            content = result["choices"][0]["message"]["content"]
            parsed = json_mod.loads(content)
            return parsed

        except json_mod.JSONDecodeError as e:
            logger.warning(f"LLM returned invalid JSON: {e}")
            return self._fallback_analysis(context)
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}, using fallback")
            return self._fallback_analysis(context)

    def _fallback_analysis(self, context: dict[str, Any]) -> dict[str, Any]:
        """Fallback template analysis when LLM is unavailable"""
        risk_level = context.get("risk_level", "中")
        stage = context.get("current_stage", "信息求证")
        signals = context.get("risk_signals", [])
        key_comments = context.get("key_comments", [])

        signal_types = [s.get("type", s.get("signal_type", "unknown")) for s in signals]

        return {
            "risk_reason": f"基于规则引擎分析：当前事件风险等级为{risk_level}，处于{stage}阶段。识别到{len(signals)}个风险信号。",
            "evolution_explanation": [
                f"事件从初始阶段演进至{stage}",
                f"检测到信号类型：{', '.join(signal_types[:5])}"
            ],
            "key_comment_explanations": [
                {"comment_id": cid, "reason": "规则引擎识别为关键评论", "risk_signal": "规则匹配"}
                for cid in key_comments[:5]
            ],
            "intervention": {
                "official_statement": "我们已注意到相关反馈，相关部门正在核实情况并将及时公布处理进展。",
                "action_items": ["核实事件真实性", "评估风险等级", "制定处置方案", "发布官方回应"],
                "avoid_phrases": ["不关我们的事", "你们自己解决", "这是惯例"],
                "responsible_department": ["学生工作部", "后勤管理处"],
                "urgency": "48小时内",
            },
            "human_review_required": risk_level in ("高", "严重"),
        }

    async def test_connection(self) -> dict[str, Any]:
        """Test LLM API connectivity"""
        start = time.time()
        try:
            result = await self.chat_completion(
                messages=[{"role": "user", "content": "回复OK即可，不要其他文字。"}],
                temperature=0,
                max_tokens=10,
                use_cache=False,
            )
            latency_ms = int((time.time() - start) * 1000)
            return {
                "success": True,
                "latency_ms": latency_ms,
                "model": result.get("model", self.model),
                "usage": result.get("usage", {}),
            }
        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            return {
                "success": False,
                "latency_ms": latency_ms,
                "error": str(e),
            }

    async def detect_sarcasm_and_homophones(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Use LLM to detect sarcasm, homophonic puns, and metaphors in comments
        that rule-based methods cannot catch.

        Args:
            texts: List of comment texts to analyze

        Returns:
            List of {text, has_sarcasm, sarcasm_type, explanation, confidence}
        """
        if not texts:
            return []

        text_block = "\n".join([f"[{i}] {t}" for i, t in enumerate(texts)])

        messages = [
            {"role": "system", "content": """你是中文网络舆情分析师，专门识别校园论坛中的：
1. 反讽/阴阳怪气（表面褒义实际贬义）
2. 谐音梗/暗语（用谐音替代敏感词）
3. 隐喻/暗示（不直接表达但有明确指向）
4. 密码式表达（拼音首字母、数字替代等）

对每条文本判断是否存在以上情况，输出JSON。"""},
            {"role": "user", "content": f"分析以下评论文本：\n\n{text_block}\n\n输出JSON数组：[{{\"index\": 数字, \"has_covert_expression\": true/false, \"type\": \"sarcasm|homophone|metaphor|coded\", \"explanation\": \"解释\", \"confidence\": 0.0-1.0}}]"}
        ]

        try:
            result = await self.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
                response_format={"type": "json_object"},
                use_cache=use_cache,
            )
            import json as json_mod
            content = result["choices"][0]["message"]["content"]
            parsed = json_mod.loads(content)
            # Handle both array and wrapped object
            if isinstance(parsed, dict):
                for v in parsed.values():
                    if isinstance(v, list):
                        return v
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception as e:
            logger.warning(f"Sarcasm detection failed: {e}")
            return []

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# Global singleton
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service