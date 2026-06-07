"""AI chat router — primary → fallback with conversation history."""

from __future__ import annotations

import logging
from typing import Any

from .completion import CompletionProvider, create_provider
from ..config import TuringConfig

logger = logging.getLogger(__name__)


class AIRouter:
    """Route chat messages through primary → fallback LLM providers."""

    def __init__(self, config: TuringConfig) -> None:
        self.system_prompt = config.ai.system_prompt
        self.history: list[dict[str, str]] = []

        # Build primary provider
        pri = config.ai.primary
        self.primary: CompletionProvider = create_provider(
            pri.provider,
            api_key=pri.api_key,
            model=pri.model,
            base_url=pri.base_url,
            temperature=pri.temperature,
            max_tokens=pri.max_tokens,
        )

        # Build fallback provider
        fb = config.ai.fallback
        self.fallback: CompletionProvider = create_provider(
            fb.provider,
            api_key=fb.api_key,
            model=fb.model,
            base_url=fb.base_url,
            temperature=fb.temperature,
            max_tokens=fb.max_tokens,
        )

    def chat(self, user_message: str, **kwargs: Any) -> str:
        """Send *user_message* through primary, falling back on failure."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_message})

        # Try primary
        try:
            reply = self.primary.complete(messages, **kwargs)
        except Exception as exc:
            logger.warning("Primary failed (%s), trying fallback", exc)
            try:
                reply = self.fallback.complete(messages, **kwargs)
            except Exception as exc2:
                logger.error("Fallback also failed: %s", exc2)
                return "I'm sorry sir, both AI systems are currently unavailable."

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": reply})

        # Keep history bounded
        if len(self.history) > 40:
            self.history = self.history[-20:]

        return reply

    def clear_history(self) -> None:
        self.history.clear()
