"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_analyze, routes_baseline, routes_events, routes_graph, routes_report, routes_llm
from .config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    print(f"Starting Campus Opinion Radar API on {settings.backend_host}:{settings.backend_port}")
    yield
    # Cleanup LLM client on shutdown
    try:
        from .services.llm_service import get_llm_service
        llm = get_llm_service()
        await llm.close()
    except Exception:
        pass
    print("Shutting down Campus Opinion Radar API")


app = FastAPI(
    title="Campus Opinion Radar API",
    description="面向校园墙场景的舆情风险演化与证据化处置平台",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(routes_events.router)
app.include_router(routes_analyze.router)
app.include_router(routes_graph.router)
app.include_router(routes_report.router)
app.include_router(routes_baseline.router)
app.include_router(routes_llm.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Campus Opinion Radar API",
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}