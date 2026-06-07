"""News skill — fetch headlines via NewsAPI."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine

logger = logging.getLogger(__name__)


class NewsSkill:
    """Fetch and read news headlines."""

    def __init__(self, tts: TTSEngine, api_key: str = "") -> None:
        self.tts = tts
        self.api_key = api_key

    def can_handle(self, query: str) -> bool:
        return "news" in query

    def handle(self, query: str) -> bool:
        topic = (
            query.replace("news about", "")
            .replace("latest news on", "")
            .replace("news", "")
            .strip()
        )
        if not topic:
            topic = "latest"
        self._fetch(topic)
        return True

    def _fetch(self, topic: str) -> None:
        self.tts.say(f"Fetching the latest news about {topic}")
        if not self.api_key:
            self.tts.say("News API key not configured, sir.")
            return
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.api_key)
            headlines = newsapi.get_top_headlines(q=topic, language="en", country="us")
            if headlines["status"] == "ok" and headlines["totalResults"] > 0:
                for i, article in enumerate(headlines["articles"][:5], start=1):
                    self.tts.say(f"News {i}: {article['title']}")
            else:
                self.tts.say("No recent news found, sir.")
        except Exception as exc:
            self.tts.say("Error fetching news, sir.")
            logger.error("News error: %s", exc)
