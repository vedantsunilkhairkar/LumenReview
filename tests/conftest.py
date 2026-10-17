"""Pytest configuration and shared fixtures for LumenReview."""

import os

import pytest

from app.core.config import Settings

# Force mock LLM and test mode
os.environ["APP_ENV"] = "test"
os.environ["LLM_PROVIDER"] = "mock"


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_env="test",
        llm_provider="mock",
        chroma_persist_dir="./data/test_chroma_db",
        database_url="sqlite+aiosqlite:///:memory:",
    )
