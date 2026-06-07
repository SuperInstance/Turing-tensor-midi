"""Band skill — voice interface to the Self-Improving Band."""

from __future__ import annotations

import re
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine
    from ..band.ensemble import Ensemble

logger = logging.getLogger(__name__)


class BandSkill:
    """Control the Self-Improving Band via voice commands."""

    def __init__(self, tts: TTSEngine, ensemble: Ensemble | None = None) -> None:
        self.tts = tts
        self.ensemble = ensemble

    def can_handle(self, query: str) -> bool:
        band_keywords = ["band", "agent", "ensemble", "blues", "jazz",
                         "spectral", "tempo", "lay out", "solo"]
        return any(kw in query for kw in band_keywords)

    def handle(self, query: str) -> bool:
        if self.ensemble is None:
            self.tts.say("The band module is not initialised, sir.")
            return True

        # "start a Bb blues with 5 agents"
        match = re.search(r"start\s+.*?(\w+)\s+(blues|jazz|swing|ballad).*?(\d+)\s*agent", query)
        if match:
            key, style, count = match.group(1), match.group(2), int(match.group(3))
            self.ensemble.start_session(key=key, style=style, agent_count=count)
            self.tts.say(f"Starting a {key} {style} session with {count} agents, sir.")
            return True

        # "tell horns to lay out"
        if "lay out" in query:
            section = self._extract_section(query)
            self.ensemble.lay_out(section)
            self.tts.say(f"Instructing {section} to lay out, sir.")
            return True

        # "what's the spectral state"
        if "spectral state" in query or "spectral" in query:
            state = self.ensemble.spectral_state()
            self.tts.say(f"The spectral state is as follows, sir. {state}")
            return True

        # "set tempo to 140"
        tempo_match = re.search(r"tempo\s+(?:to\s+)?(\d+)", query)
        if tempo_match:
            bpm = float(tempo_match.group(1))
            self.ensemble.set_tempo(bpm)
            self.tts.say(f"Tempo set to {bpm:.0f} BPM, sir.")
            return True

        self.tts.say("I didn't quite catch the band instruction, sir.")
        return True

    @staticmethod
    def _extract_section(query: str) -> str:
        sections = ["horns", "rhythm", "bass", "drums", "keys", "guitar", "brass"]
        for s in sections:
            if s in query:
                return s
        return "all"
