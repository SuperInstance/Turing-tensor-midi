"""System skill — greetings, time, identity, control."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.tts import TTSEngine


class SystemSkill:
    """Handle system-level commands: greetings, time, identity."""

    def __init__(self, tts: TTSEngine) -> None:
        self.tts = tts

    def can_handle(self, query: str) -> bool:
        triggers = [
            "hi turing", "hello turing",
            "who are you", "introduce yourself",
            "what's the time", "time",
        ]
        return any(t in query for t in triggers)

    def handle(self, query: str) -> bool:
        if "hi turing" in query or "hello turing" in query:
            self.tts.say("Good day, sir. How may I assist you?")
        elif "who are you" in query or "introduce yourself" in query:
            self.tts.say(
                "I am Turing, your personal AI assistant — designed to serve "
                "you with precision and courtesy, sir."
            )
        elif "time" in query:
            now = datetime.datetime.now()
            self.tts.say(
                f"Sir, the time is {now.strftime('%H')} hours "
                f"and {now.strftime('%M')} minutes."
            )
        else:
            return False
        return True
