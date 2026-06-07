"""Site shortcuts registry — loaded from YAML data."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class SiteRegistry:
    """Lookup website URLs by name from YAML configuration."""

    def __init__(self, sites: dict[str, str] | None = None) -> None:
        self._sites: dict[str, str] = sites or {}

    @classmethod
    def from_yaml(cls, path: Path | str | None = None) -> SiteRegistry:
        """Load sites from a YAML file mapping names to URLs."""
        yaml_path = Path(path) if path else _CONFIG_DIR / "sites.yaml"
        if not yaml_path.exists():
            logger.warning("Sites YAML not found: %s", yaml_path)
            return cls()
        with open(yaml_path) as f:
            data = yaml.safe_load(f) or {}
        sites: dict[str, str] = {}
        for entry in data.get("sites", []):
            if isinstance(entry, dict):
                for name, url in entry.items():
                    sites[name.lower().strip()] = str(url)
        return cls(sites)

    def lookup(self, name: str) -> str | None:
        """Return URL for *name*, or None."""
        return self._sites.get(name.lower().strip())

    def all_sites(self) -> dict[str, str]:
        """Return copy of all registered sites."""
        return dict(self._sites)

    def count(self) -> int:
        return len(self._sites)
