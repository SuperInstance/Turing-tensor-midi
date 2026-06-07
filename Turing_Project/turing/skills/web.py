"""Web skill — open sites, search, navigate."""

from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine
    from ..sites import SiteRegistry


class WebSkill:
    """Handle web-related voice commands."""

    def __init__(self, tts: TTSEngine, sites: SiteRegistry) -> None:
        self.tts = tts
        self.sites = sites

    def can_handle(self, query: str) -> bool:
        return query.startswith("open ") or query.startswith("search for ") or "search" in query

    def handle(self, query: str) -> bool:
        """Return True if the query was handled."""
        if query.startswith("search for "):
            term = query.replace("search for ", "").strip()
            if term:
                self.tts.say(f"Searching for {term} on Google.")
                webbrowser.open(f"https://www.google.com/search?q={term}")
                return True

        if query.startswith("open "):
            site_name = query.replace("open ", "").strip()
            url = self.sites.lookup(site_name)
            if url:
                self.tts.say(f"Opening {site_name}, sir.")
                webbrowser.open(url)
                return True
            # Generic URL construction
            clean = site_name.replace(" ", "")
            url = f"https://{clean}" if not clean.startswith("http") else clean
            self.tts.say(f"Opening {site_name}, sir.")
            webbrowser.open(url)
            return True

        return False
