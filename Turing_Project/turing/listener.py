"""Wake-word listener — passive and active listening modes."""

from __future__ import annotations

import datetime
import logging
import threading
import time

from .config import TuringConfig
from .engine.speech import SpeechEngine
from .engine.tts import TTSEngine
from .router import CommandRouter

logger = logging.getLogger(__name__)

# Deactivation hotwords
_DEACTIVATE = {"thank you turing", "go to idle turing", "sleep turing"}
_SHUTDOWN = {"stop turing", "shutdown turing", "exit", "quit"}


class TuringListener:
    """Main listener with passive wake-word + active command modes."""

    def __init__(self, config: TuringConfig | None = None) -> None:
        self.config = config or TuringConfig()
        self.tts = TTSEngine(
            rate=self.config.tts.rate,
            volume=self.config.tts.volume,
            voice_preference=self.config.tts.voice_preference,
        )
        self.speech = SpeechEngine(
            language=self.config.listener.language,
            timeout=self.config.listener.timeout,
            phrase_limit=self.config.listener.phrase_limit,
        )
        self.router = CommandRouter(self.config)
        self._running = False
        self._active = False

    @property
    def running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False
        self._active = False

    def run(self) -> None:
        """Main entry: startup → passive loop."""
        self._running = True
        self._startup()
        self._passive_loop()

    def _startup(self) -> None:
        """Print banner and speak greeting."""
        print("=" * 70)
        print("             🤖  T U R I N G   T E R M I N A L")
        print("=" * 70)
        for line in ["Initializing systems...", "Loading modules...",
                      "Activating voice engine..."]:
            self.tts.say(line)
            time.sleep(0.3)

        hour = datetime.datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        c_time = datetime.datetime.now().strftime("%H:%M")
        self.tts.say(
            f"{greeting}, sir. The current time is {c_time}. "
            "Turing is online and fully operational."
        )
        print("\n🎧 Passive listening mode — say 'Turing' to wake me up.\n")

    def _passive_loop(self) -> None:
        """Listen for wake word in the background."""
        while self._running:
            result = self.speech.listen()
            if not result.text:
                continue
            if self.config.listener.wake_word in result.text and not self._active:
                self._active = True
                self.tts.say("Yes sir?")
                self._active_loop()
            elif any(w in result.text for w in _SHUTDOWN):
                self.tts.say("Understood, sir. Shutting down systems.")
                self._running = False

    def _active_loop(self) -> None:
        """Process commands until deactivation."""
        self.tts.say("Turing online and ready, sir.")
        while self._active and self._running:
            result = self.speech.listen()
            query = result.text
            if not query:
                continue

            if any(kw in query for kw in _DEACTIVATE):
                self.tts.say("Understood, sir. Going to standby mode.")
                self._active = False
                break

            if any(kw in query for kw in _SHUTDOWN):
                self.tts.say("Understood, sir. Shutting down completely.")
                self._active = False
                self._running = False
                break

            self.router.dispatch(query)
