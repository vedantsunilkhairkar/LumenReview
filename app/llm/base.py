"""Base LLM Provider abstract interface."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_model: type[T] | None = None,
        temperature: float = 0.0,
    ) -> T | str:
        """Generate response from LLM, optionally structured to a Pydantic schema."""
        pass
