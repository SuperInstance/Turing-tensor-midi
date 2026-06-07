"""Tests for skill modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from turing.engine.tts import TTSEngine
from turing.skills.web import WebSkill
from turing.skills.weather import WeatherSkill
from turing.skills.news import NewsSkill
from turing.skills.music import MusicSkill
from turing.skills.system import SystemSkill
from turing.sites import SiteRegistry


@pytest.fixture
def tts() -> TTSEngine:
    engine = TTSEngine()
    engine._engine = None  # prevent actual init
    engine.say = MagicMock()  # type: ignore[method-assign]
    return engine


@pytest.fixture
def sites() -> SiteRegistry:
    return SiteRegistry({"youtube": "https://www.youtube.com", "github": "https://github.com"})


class TestWebSkill:
    def test_can_handle_open(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        skill = WebSkill(tts, sites)
        assert skill.can_handle("open youtube")

    def test_can_handle_search(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        skill = WebSkill(tts, sites)
        assert skill.can_handle("search for cats")

    def test_cannot_handle_random(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        skill = WebSkill(tts, sites)
        assert not skill.can_handle("what's the time")

    def test_handle_open_known(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        skill = WebSkill(tts, sites)
        with patch("turing.skills.web.webbrowser.open") as mock:
            result = skill.handle("open youtube")
            assert result is True
            mock.assert_called_with("https://www.youtube.com")

    def test_handle_search(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        skill = WebSkill(tts, sites)
        with patch("turing.skills.web.webbrowser.open") as mock:
            result = skill.handle("search for python")
            assert result is True
            assert "python" in mock.call_args[0][0]


class TestSystemSkill:
    def test_can_handle_greeting(self, tts: TTSEngine) -> None:
        skill = SystemSkill(tts)
        assert skill.can_handle("hello turing")

    def test_can_handle_time(self, tts: TTSEngine) -> None:
        skill = SystemSkill(tts)
        assert skill.can_handle("what's the time")

    def test_handle_identity(self, tts: TTSEngine) -> None:
        skill = SystemSkill(tts)
        result = skill.handle("who are you")
        assert result is True
        tts.say.assert_called_once()

    def test_cannot_handle_other(self, tts: TTSEngine) -> None:
        skill = SystemSkill(tts)
        assert not skill.can_handle("play music")


class TestWeatherSkill:
    def test_can_handle(self, tts: TTSEngine) -> None:
        skill = WeatherSkill(tts, api_key="test")
        assert skill.can_handle("what's the weather in Paris")

    def test_cannot_handle(self, tts: TTSEngine) -> None:
        skill = WeatherSkill(tts)
        assert not skill.can_handle("what's the time")

    def test_handle_extracts_location(self, tts: TTSEngine) -> None:
        skill = WeatherSkill(tts, api_key="test")
        with patch.object(skill, "_report") as mock:
            result = skill.handle("weather in Tokyo")
            assert result is True
            mock.assert_called_once_with("Tokyo")


class TestNewsSkill:
    def test_can_handle(self, tts: TTSEngine) -> None:
        skill = NewsSkill(tts, api_key="test")
        assert skill.can_handle("news about AI")

    def test_handle(self, tts: TTSEngine) -> None:
        skill = NewsSkill(tts, api_key="test")
        with patch.object(skill, "_fetch") as mock:
            result = skill.handle("news about space")
            assert result is True
            mock.assert_called_once_with("space")


class TestMusicSkill:
    def test_can_handle(self, tts: TTSEngine) -> None:
        skill = MusicSkill(tts)
        assert skill.can_handle("play bohemian rhapsody on youtube")

    def test_cannot_handle(self, tts: TTSEngine) -> None:
        skill = MusicSkill(tts)
        assert not skill.can_handle("open youtube")
