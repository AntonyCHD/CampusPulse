"""
LLM API Routes - Proxy endpoints for LLM operations

Per design doc M8: LLM structured analysis with caching and fallback
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/llm", tags=["LLM"])


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    temperature: float = 0.3
    max_tokens: int = 2048
    use_cache: bool = True


class AnalyzeRequest(BaseModel):
    event_summary: str = ""
    risk_score: float = 0.0
    risk_level: str = "中"
    current_stage: str = "信息求证"
    risk_signals: list[dict] = []
    key_comments: list[str] = []
    evidence: list[dict] = []
    baseline_result: dict | None = None
    use_cache: bool = True


class SarcasmRequest(BaseModel):
    texts: list[str]
    use_cache: bool = True


@router.post("/chat")
async def chat_completion(req: ChatRequest):
    """Proxy chat completion to configured LLM provider"""
    llm = get_llm_service()
    if not llm.is_configured:
        raise HTTPException(status_code=400, detail="LLM API key not configured")
    try:
        result = await llm.chat_completion(
            messages=req.messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            use_cache=req.use_cache,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/analyze")
async def structured_analysis(req: AnalyzeRequest):
    """M8: Structured risk analysis with LLM"""
    llm = get_llm_service()
    if not llm.is_configured:
        # Return fallback directly
        return llm._fallback_analysis(req.model_dump())
    try:
        result = await llm.structured_analysis(
            context=req.model_dump(),
            use_cache=req.use_cache,
        )
        return result
    except Exception as e:
        return llm._fallback_analysis(req.model_dump())


@router.post("/detect-sarcasm")
async def detect_sarcasm(req: SarcasmRequest):
    """Detect sarcasm, homophonic puns, and metaphors in texts"""
    llm = get_llm_service()
    if not llm.is_configured:
        raise HTTPException(status_code=400, detail="LLM API key not configured")
    try:
        result = await llm.detect_sarcasm_and_homophones(
            texts=req.texts,
            use_cache=req.use_cache,
        )
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/status")
async def llm_status():
    """Check LLM configuration and connectivity"""
    llm = get_llm_service()
    if not llm.is_configured:
        return {
            "configured": False,
            "model": "",
            "message": "LLM API key not configured",
        }
    try:
        test = await llm.test_connection()
        return {
            "configured": True,
            "model": llm.model,
            "connected": test["success"],
            "latency_ms": test.get("latency_ms", 0),
            "error": test.get("error") if not test["success"] else None,
        }
    except Exception as e:
        return {
            "configured": True,
            "model": llm.model,
            "connected": False,
            "error": str(e),
        }


@router.post("/test")
async def test_connection():
    """Test LLM API connection"""
    llm = get_llm_service()
    if not llm.is_configured:
        raise HTTPException(status_code=400, detail="LLM API key not configured")
    return await llm.test_connection()