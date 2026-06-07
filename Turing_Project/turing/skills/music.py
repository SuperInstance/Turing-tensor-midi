"""Music skill — play media via pywhatkit."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine


class MusicSkill:
    """Play music and media via YouTube / web."""

    def __init__(self, tts: TTSEngine) -> None:
        self.tts = tts

    def can_handle(self, query: str) -> bool:
        return "play" in query and ("youtube" in query or "music" in query or "song" in query)

    def handle(self, query: str) -> bool:
        video = query.replace("play on youtube", "").replace("play", "").strip()
        if video:
            self.tts.say(f"Playing {video} on YouTube, sir.")
            try:
                import pywhatkit
                pywhatkit.playonyt(video)
            except Exception:
                self.tts.say("Unable to play that, sir.")
            return True
        self.tts.say("Please specify what to play, sir.")
        return True
