"""LLM Provider Factory."""

from app.core.config import settings
from app.core.logging import logger
from app.llm.base import BaseLLMProvider
from app.llm.mock import MockLLM
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.providers.gemini import GeminiProvider
from app.llm.providers.openai import OpenAIProvider


def get_llm_provider(
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> BaseLLMProvider:
    name = (provider_name or settings.llm_provider).lower()

    if name == "mock":
        return MockLLM()
    elif name == "gemini":
        key = api_key or settings.gemini_api_key
        if not key:
            logger.warning("Gemini API key not found. Falling back to MockLLM.")
            return MockLLM()
        return GeminiProvider(api_key=key, model=model)
    elif name == "openai":
        key = api_key or settings.openai_api_key
        if not key:
            logger.warning("OpenAI API key not found. Falling back to MockLLM.")
            return MockLLM()
        return OpenAIProvider(api_key=key, model=model)
    elif name == "anthropic":
        key = api_key or settings.anthropic_api_key
        if not key:
            logger.warning("Anthropic API key not found. Falling back to MockLLM.")
            return MockLLM()
        return AnthropicProvider(api_key=key, model=model)
    else:
        logger.warning("Unknown provider '%s'. Using MockLLM.", name)
        return MockLLM()
