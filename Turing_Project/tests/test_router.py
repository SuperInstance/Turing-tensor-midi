"""Tests for the command router."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from turing.config import TuringConfig
from turing.router import CommandRouter


@pytest.fixture
def config() -> TuringConfig:
    cfg = TuringConfig()
    cfg.ai.primary.api_key = "test-key"
    cfg.ai.fallback.api_key = "test-key"
    return cfg


@pytest.fixture
def router(config: TuringConfig) -> CommandRouter:
    with patch("turing.engine.tts.TTSEngine.say"):
        return CommandRouter(config)


class TestCommandRouter:
    def test_dispatch_empty_query(self, router: CommandRouter) -> None:
        result = router.dispatch("")
        assert result is None

    def test_system_greeting(self, router: CommandRouter) -> None:
        # Should not raise
        router.dispatch("hello turing")

    def test_time_query(self, router: CommandRouter) -> None:
        router.dispatch("what's the time")

    def test_identity_query(self, router: CommandRouter) -> None:
        router.dispatch("who are you")

    def test_search_command(self, router: CommandRouter) -> None:
        with patch("turing.skills.web.webbrowser.open") as mock_open:
            router.dispatch("search for python tutorials")
            mock_open.assert_called_once()

    def test_open_known_site(self, router: CommandRouter) -> None:
        with patch("turing.skills.web.webbrowser.open") as mock_open:
            router.dispatch("open youtube")
            mock_open.assert_called_once()

    def test_open_unknown_site(self, router: CommandRouter) -> None:
        with patch("turing.skills.web.webbrowser.open") as mock_open:
            router.dispatch("open example.com")
            mock_open.assert_called_once()

    def test_weather_query(self, router: CommandRouter) -> None:
        with patch.object(router.skills[2], "_report") as mock_report:
            router.dispatch("what's the weather in London")
            mock_report.assert_called_once_with("London")

    def test_news_query(self, router: CommandRouter) -> None:
        with patch.object(router.skills[3], "_fetch") as mock_fetch:
            router.dispatch("news about technology")
            mock_fetch.assert_called_once_with("technology")

    def test_register_custom_skill(self, router: CommandRouter) -> None:
        skill = MagicMock()
        skill.can_handle.return_value = False
        router.register_skill(skill)
        assert skill in router.skills

    def test_ai_fallback_on_unknown_query(self, router: CommandRouter) -> None:
        with patch.object(router.ai, "chat", return_value="Test response") as mock_chat:
            router.dispatch("tell me about quantum physics")
            mock_chat.assert_called_once()
