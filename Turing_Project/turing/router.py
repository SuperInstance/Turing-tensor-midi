"""Command router — parse intent, dispatch to skills."""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

from .engine.tts import TTSEngine
from .engine.ai import AIRouter
from .sites import SiteRegistry
from .skills.web import WebSkill
from .skills.weather import WeatherSkill
from .skills.news import NewsSkill
from .skills.music import MusicSkill
from .skills.system import SystemSkill
from .skills.band import BandSkill
from .config import TuringConfig

logger = logging.getLogger(__name__)


@runtime_checkable
class Skill(Protocol):
    def can_handle(self, query: str) -> bool: ...
    def handle(self, query: str) -> bool: ...


class CommandRouter:
    """Parse voice commands and dispatch to registered skills."""

    def __init__(self, config: TuringConfig) -> None:
        self.config = config
        self.tts = TTSEngine(
            rate=config.tts.rate,
            volume=config.tts.volume,
            voice_preference=config.tts.voice_preference,
        )
        self.sites = SiteRegistry.from_yaml()
        self.ai = AIRouter(config)

        # Ordered skill chain
        self.skills: list[Skill] = [
            SystemSkill(self.tts),
            WebSkill(self.tts, self.sites),
            WeatherSkill(self.tts, config.weather_api_key),
            NewsSkill(self.tts, config.news_api_key),
            MusicSkill(self.tts),
        ]

        # Optional band skill
        if config.band.enabled:
            from .band.ensemble import Ensemble
            ensemble = Ensemble(config.band)
            self.skills.append(BandSkill(self.tts, ensemble))

    def dispatch(self, query: str) -> str | None:
        """Try each skill; fall back to AI chat. Returns response text or None."""
        if not query:
            return None

        for skill in self.skills:
            if skill.can_handle(query):
                handled = skill.handle(query)
                if handled:
                    return None  # Skill already spoke via TTS

        # Fallback: AI chat
        response = self.ai.chat(query)
        self.tts.say(response)
        return response

    def register_skill(self, skill: Skill) -> None:
        """Add a skill to the chain."""
        self.skills.append(skill)
