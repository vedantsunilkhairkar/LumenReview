"""OpenAI Provider implementation using direct REST API."""

import json
from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger
from app.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate(
        self,
        prompt: str,
        response_model: type[T] | None = None,
        temperature: float = 0.0,
    ) -> T | str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if response_model is not None:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        try:
            raw_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error("Unexpected OpenAI API response structure: %s", data)
            raise RuntimeError("Invalid response structure from OpenAI API") from e

        if response_model is not None:
            clean_text = raw_text.strip()
            parsed = json.loads(clean_text)
            return response_model.model_validate(parsed)

        return raw_text
