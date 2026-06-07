"""Configuration loader — env vars + YAML with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).resolve().parent.parent  # Turing_Project/
_CONFIG_DIR = _ROOT / "config"


@dataclass
class AIProviderConfig:
    provider: str = "zai"
    model: str = "glm-5.1"
    base_url: str = "https://api.z.ai/v1"
    api_key: str = ""
    temperature: float = 0.6
    max_tokens: int = 300


@dataclass
class AIConfig:
    primary: AIProviderConfig = field(default_factory=AIProviderConfig)
    fallback: AIProviderConfig = field(default_factory=lambda: AIProviderConfig(
        provider="deepinfra",
        model="Seed-2.0-mini",
        base_url="https://api.deepinfra.com/v1/openai",
    ))
    system_prompt: str = (
        "You are Turing, a polite, intelligent, British AI assistant. "
        "Always address the user as 'sir' and respond formally but naturally."
    )


@dataclass
class ListenerConfig:
    wake_word: str = "turing"
    timeout: int = 8
    phrase_limit: int = 10
    language: str = "en-GB"


@dataclass
class TTSConfig:
    rate: int = 165
    volume: float = 1.0
    voice_preference: str = "en-gb"


@dataclass
class MidiConfig:
    enabled: bool = False
    input_port: int | None = None
    output_port: int | None = None


@dataclass
class BandConfig:
    enabled: bool = False
    default_agents: int = 4
    conservation_gamma: float = 0.5
    tempo_bpm: float = 120.0


@dataclass
class TuringConfig:
    ai: AIConfig = field(default_factory=AIConfig)
    listener: ListenerConfig = field(default_factory=ListenerConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    midi: MidiConfig = field(default_factory=MidiConfig)
    band: BandConfig = field(default_factory=BandConfig)
    weather_api_key: str = ""
    news_api_key: str = ""


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge *override* into *base* recursively."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def _resolve_env(config: TuringConfig) -> None:
    """Overlay environment variables onto config."""
    config.ai.primary.api_key = os.getenv("ZAI_API_KEY", config.ai.primary.api_key)
    config.ai.fallback.api_key = os.getenv("DEEPINFRA_API_KEY", config.ai.fallback.api_key)
    config.weather_api_key = os.getenv("WEATHER_API_KEY", config.weather_api_key)
    config.news_api_key = os.getenv("NEWS_API_KEY", config.news_api_key)


def _apply_yaml_dict(cfg: TuringConfig, data: dict[str, Any]) -> TuringConfig:
    """Apply a raw yaml dict to a TuringConfig dataclass."""
    if "ai" in data:
        ai = data["ai"]
        if "primary" in ai:
            for k, v in ai["primary"].items():
                if hasattr(cfg.ai.primary, k):
                    setattr(cfg.ai.primary, k, v)
        if "fallback" in ai:
            for k, v in ai["fallback"].items():
                if hasattr(cfg.ai.fallback, k):
                    setattr(cfg.ai.fallback, k, v)
        if "system_prompt" in ai:
            cfg.ai.system_prompt = ai["system_prompt"]
    if "listener" in data:
        for k, v in data["listener"].items():
            if hasattr(cfg.listener, k):
                setattr(cfg.listener, k, v)
    if "tts" in data:
        for k, v in data["tts"].items():
            if hasattr(cfg.tts, k):
                setattr(cfg.tts, k, v)
    if "midi" in data:
        for k, v in data["midi"].items():
            if hasattr(cfg.midi, k):
                setattr(cfg.midi, k, v)
    if "band" in data:
        for k, v in data["band"].items():
            if hasattr(cfg.band, k):
                setattr(cfg.band, k, v)
    return cfg


def load_config(path: Path | str | None = None) -> TuringConfig:
    """Load configuration from defaults → YAML → env vars."""
    cfg = TuringConfig()

    # 1. Default YAML
    default_path = _CONFIG_DIR / "default.yaml"
    yaml_data: dict[str, Any] = {}
    if default_path.exists():
        with open(default_path) as f:
            yaml_data = yaml.safe_load(f) or {}

    # 2. User override YAML
    user_path = Path(path) if path else _CONFIG_DIR / "user.yaml"
    if user_path.exists():
        with open(user_path) as f:
            user_data = yaml.safe_load(f) or {}
        yaml_data = _deep_merge(yaml_data, user_data)

    # 3. Apply yaml to config
    if yaml_data:
        cfg = _apply_yaml_dict(cfg, yaml_data)

    # 4. Environment variables (highest priority)
    _resolve_env(cfg)

    return cfg
