"""Tests for site shortcuts registry."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from turing.sites import SiteRegistry


class TestSiteRegistry:
    def test_empty_registry(self) -> None:
        reg = SiteRegistry()
        assert reg.count() == 0
        assert reg.lookup("youtube") is None

    def test_lookup(self) -> None:
        reg = SiteRegistry({"youtube": "https://www.youtube.com"})
        assert reg.lookup("youtube") == "https://www.youtube.com"

    def test_case_insensitive(self) -> None:
        reg = SiteRegistry({"youtube": "https://www.youtube.com"})
        assert reg.lookup("YouTube") == "https://www.youtube.com"
        assert reg.lookup("YOUTUBE") == "https://www.youtube.com"

    def test_missing_site(self) -> None:
        reg = SiteRegistry({"youtube": "https://www.youtube.com"})
        assert reg.lookup("nonexistent") is None

    def test_all_sites(self) -> None:
        data = {"a": "http://a.com", "b": "http://b.com"}
        reg = SiteRegistry(data)
        assert reg.all_sites() == data

    def test_from_yaml(self, tmp_path: Path) -> None:
        yaml_data = {
            "sites": [
                {"youtube": "https://www.youtube.com"},
                {"github": "https://github.com"},
                {"google": "https://www.google.com"},
            ]
        }
        yaml_file = tmp_path / "sites.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(yaml_data, f)

        reg = SiteRegistry.from_yaml(yaml_file)
        assert reg.count() == 3
        assert reg.lookup("youtube") == "https://www.youtube.com"
        assert reg.lookup("github") == "https://github.com"

    def test_from_missing_yaml(self) -> None:
        reg = SiteRegistry.from_yaml("/nonexistent/path.yaml")
        assert reg.count() == 0
