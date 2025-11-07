from __future__ import annotations

import os
from typing import Any, Dict, List

from tenacity import retry, stop_after_attempt, wait_exponential


class BaseChatLLM:
    """Minimal protocol for chat-based LLM providers."""

    async def ainvoke(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        raise NotImplementedError


class MockChatLLM(BaseChatLLM):
    """Deterministic LLM that reflects insights without external calls."""

    async def ainvoke(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        content = messages[-1]["content"]
        return f"[mock-llm-response]: {content[:256]}"


class OpenAIChatLLM(BaseChatLLM):
    """Thin async wrapper around OpenAI's Chat Completions API."""

    def __init__(
        self,
        model: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
        api_key: str | None = None,
    ) -> None:
        try:
            from openai import AsyncOpenAI  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "openai package is required for OpenAIChatLLM."
            ) from exc

        self._client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._model = model
        self._temperature = temperature
        self._top_p = top_p
        self._max_tokens = max_tokens

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def ainvoke(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            top_p=self._top_p,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content or ""


def build_llm(provider: str, **kwargs: Any) -> BaseChatLLM:
    if provider == "mock":
        return MockChatLLM()
    if provider == "openai":
        return OpenAIChatLLM(**kwargs)
    raise ValueError(f"Unsupported LLM provider '{provider}'.")
