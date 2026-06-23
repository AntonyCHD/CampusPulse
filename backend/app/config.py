"""Configuration management."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Configuration
    api_base_url: str = "http://localhost:8000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 8501

    # LLM Configuration
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Embedding Model
    embedding_model: str = "BAAI/bge-m3"
    embedding_device: str = "cpu"

    # Vector Store
    vector_store_path: str = "./cache/vector_store"
    chroma_persist_directory: str = "./cache/chroma_db"

    # Database
    db_path: str = "./data/campus_opinion.db"

    # Cache Configuration
    enable_cache: bool = True
    cache_dir: str = "./cache"
    llm_cache_dir: str = "./cache/llm_responses"
    demo_cache_dir: str = "./cache/demo_reports"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./outputs/logs/app.log"

    # Analysis Configuration
    top_n_comments: int = 20
    semantic_threshold: float = 0.80
    topic_threshold: float = 0.78
    resonance_threshold: float = 0.55

    # Safety & Privacy
    enable_anonymization: bool = True
    salt_key: str = "default_salt_change_in_production"

    # Demo Mode
    default_mode: Literal["cached", "realtime"] = "cached"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
