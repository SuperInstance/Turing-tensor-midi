"""Completion provider protocol and implementations — z.ai + DeepInfra only."""

from __future__ import annotations

import json
import logging
from typing import Protocol, runtime_checkable

import requests

logger = logging.getLogger(__name__)


@runtime_checkable
class CompletionProvider(Protocol):
    """Abstract completion provider interface."""

    def complete(self, messages: list[dict], **kwargs: object) -> str:
        ...


class _BaseHTTPProvider:
    """Shared HTTP logic for OpenAI-compatible endpoints."""

    def __init__(self, base_url: str, api_key: str, model: str,
                 temperature: float = 0.6, max_tokens: int = 300,
                 timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _request(self, messages: list[dict], **kwargs: object) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": float(kwargs.get("temperature", self.temperature)),
            "max_tokens": int(kwargs.get("max_tokens", self.max_tokens)),
        }
        url = f"{self.base_url}/chat/completions"
        resp = requests.post(url, headers=headers, data=json.dumps(payload),
                             timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def complete(self, messages: list[dict], **kwargs: object) -> str:
        try:
            result = self._request(messages, **kwargs)
            return result["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            logger.error("%s error: %s", self.__class__.__name__, exc)
            raise


class ZAIProvider(_BaseHTTPProvider):
    """z.ai GLM-5.1 — PRIMARY provider.

    base_url: https://api.z.ai/v1
    """

    def __init__(self, api_key: str, model: str = "glm-5.1",
                 base_url: str = "https://api.z.ai/v1",
                 **kwargs: object) -> None:
        super().__init__(base_url=base_url, api_key=api_key, model=model, **kwargs)


class DeepInfraProvider(_BaseHTTPProvider):
    """DeepInfra — FALLBACK provider.

    base_url: https://api.deepinfra.com/v1/openai
    Models: Seed-2.0-mini, Gemma-4-31B, Nemotron-120B, Qwen-3.6, Hermes-405B
    """

    def __init__(self, api_key: str, model: str = "Seed-2.0-mini",
                 base_url: str = "https://api.deepinfra.com/v1/openai",
                 **kwargs: object) -> None:
        super().__init__(base_url=base_url, api_key=api_key, model=model, **kwargs)


PROVIDERS: dict[str, type[_BaseHTTPProvider]] = {
    "zai": ZAIProvider,
    "deepinfra": DeepInfraProvider,
}


def create_provider(name: str, **kwargs: object) -> _BaseHTTPProvider:
    """Factory: create a provider by name."""
    cls = PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown provider: {name!r}. Available: {list(PROVIDERS)}")
    return cls(**kwargs)  # type: ignore[arg-type]
