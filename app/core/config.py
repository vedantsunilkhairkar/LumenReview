"""Application settings and configuration management via Pydantic Settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_name: str = "LumenReview"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "production"] = "development"
    api_port: int = 8000
    ui_port: int = 8501
    log_level: str = "INFO"

    # Security
    api_key: str = "lumen-dev-secret-key-2026"
    allow_anonymous: bool = True

    # Database & Storage
    database_url: str = "sqlite+aiosqlite:///./data/lumenreview.db"
    chroma_persist_dir: str = "./data/chroma_db"

    # LLM Settings
    llm_provider: Literal["mock", "gemini", "openai", "anthropic"] = "mock"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    gemini_model: str = "gemini-1.5-flash"
    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # RAG Settings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    top_k_retrieval: int = 5
    min_citation_similarity: float = 0.85
    enable_bm25_rerank: bool = True

    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)

    @property
    def regulations_dir(self) -> Path:
        return self.base_dir / "data" / "regulations"

    @property
    def eval_data_dir(self) -> Path:
        return self.base_dir / "data" / "eval"


settings = Settings()
