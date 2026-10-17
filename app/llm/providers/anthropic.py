"""Anthropic Provider implementation using REST API."""

import json
from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger
from app.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        self.endpoint = "https://api.anthropic.com/v1/messages"

    def generate(
        self,
        prompt: str,
        response_model: type[T] | None = None,
        temperature: float = 0.0,
    ) -> T | str:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            raw_text = data["content"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error("Unexpected Anthropic API response structure: %s", data)
            raise RuntimeError("Invalid response structure from Anthropic API") from e

        if response_model is not None:
            clean_text = raw_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()
            parsed = json.loads(clean_text)
            return response_model.model_validate(parsed)

        return raw_text
