"""Weather skill — fetch and report weather for a location."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine

logger = logging.getLogger(__name__)


class WeatherSkill:
    """Report weather conditions via Visual Crossing API."""

    def __init__(self, tts: TTSEngine, api_key: str = "") -> None:
        self.tts = tts
        self.api_key = api_key

    def can_handle(self, query: str) -> bool:
        return "weather" in query and "in" in query

    def handle(self, query: str) -> bool:
        location = query.replace("what's the weather in", "").replace("weather in", "").strip()
        if not location:
            return False
        self._report(location)
        return True

    def _report(self, location: str) -> None:
        self.tts.say(f"Fetching weather details for {location}")
        if not self.api_key:
            self.tts.say("Weather API key not configured, sir.")
            return
        try:
            url = (
                f"https://weather.visualcrossing.com/VisualCrossingWebServices"
                f"/rest/services/timeline/{location}?key={self.api_key}&unitGroup=metric"
            )
            data = requests.get(url, timeout=15).json()
            if "days" in data:
                today = data["days"][0]
                report = (
                    f"The current temperature in {location} is {today['temp']}°C. "
                    f"Weather: {today['conditions']}. Humidity: {today['humidity']}%. "
                    f"Wind: {today['windspeed']} km/h."
                )
                self.tts.say(report)
            else:
                self.tts.say("Sorry, I couldn't retrieve weather data, sir.")
        except Exception as exc:
            self.tts.say("Error fetching weather, sir.")
            logger.error("Weather error: %s", exc)
