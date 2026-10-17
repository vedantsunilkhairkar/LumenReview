"""Scaffolding and configuration verification tests."""

from app.core.config import settings
from app.core.cost import calculate_cost, estimate_tokens
from app.core.logging import logger


def test_settings_load():
    assert settings.app_name == "LumenReview"
    assert settings.llm_provider in ["mock", "gemini", "openai", "anthropic"]
    assert settings.top_k_retrieval > 0


def test_token_and_cost_estimation():
    text = "Requirement: Headlamp shall provide minimum 1000 lumens in low-beam mode."
    tokens = estimate_tokens(text)
    assert tokens > 0

    cost = calculate_cost(prompt_tokens=1000, completion_tokens=500, model="gemini-1.5-flash")
    assert cost > 0.0

    mock_cost = calculate_cost(prompt_tokens=1000, completion_tokens=500, model="mock")
    assert mock_cost == 0.0


def test_logger_initialization():
    assert logger.name == "lumenreview"
