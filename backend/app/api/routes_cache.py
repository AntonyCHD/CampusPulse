"""Cache management API routes."""

from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/cache", tags=["cache"])


def _count_files(directory: str) -> int:
    path = Path(directory)
    if not path.exists():
        return 0
    return sum(1 for f in path.rglob("*") if f.is_file())


@router.get("/stats")
async def cache_stats():
    return {
        "llm_responses": _count_files("./cache/llm_responses"),
        "demo_reports": _count_files("./cache/demo_reports"),
        "embeddings": _count_files("./cache/embeddings"),
    }
