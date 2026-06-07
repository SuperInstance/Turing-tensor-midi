"""Tests for configuration loading."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from turing.config import TuringConfig, load_config, _deep_merge


class TestDeepMerge:
    def test_simple_merge(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"y": 3, "z": 4}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 3, "z": 4}}


class TestTuringConfig:
    def test_defaults(self) -> None:
        cfg = TuringConfig()
        assert cfg.ai.primary.provider == "zai"
        assert cfg.ai.primary.model == "glm-5.1"
        assert cfg.ai.fallback.provider == "deepinfra"
        assert cfg.listener.wake_word == "turing"
        assert cfg.tts.rate == 165

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZAI_API_KEY", "zai-test-key")
        monkeypatch.setenv("DEEPINFRA_API_KEY", "di-test-key")
        cfg = load_config()
        assert cfg.ai.primary.api_key == "zai-test-key"
        assert cfg.ai.fallback.api_key == "di-test-key"

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        yaml_content = {
            "ai": {
                "primary": {"model": "test-model", "temperature": 0.9},
            },
            "listener": {"wake_word": "jarvis"},
        }
        yaml_file = tmp_path / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(yaml_content, f)

        cfg = load_config(yaml_file)
        assert cfg.ai.primary.model == "test-model"
        assert cfg.ai.primary.temperature == 0.9
        assert cfg.listener.wake_word == "jarvis"

    def test_weather_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEATHER_API_KEY", "weather-key")
        cfg = load_config()
        assert cfg.weather_api_key == "weather-key"
