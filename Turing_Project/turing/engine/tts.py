"""Text-to-speech via pyttsx3 with British voice preference."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-speech with fallback to OS-native synthesis."""

    def __init__(self, rate: int = 165, volume: float = 1.0,
                 voice_preference: str = "en-gb") -> None:
        self.rate = rate
        self.volume = volume
        self.voice_preference = voice_preference
        self._engine = None

    def _init_engine(self) -> None:
        """Lazy-init to avoid issues in headless environments."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)
            for voice in self._engine.getProperty("voices"):
                vid = voice.id.lower()
                vname = voice.name.lower()
                if self.voice_preference in vid and "male" in vname:
                    self._engine.setProperty("voice", voice.id)
                    break
        except Exception as exc:
            logger.warning("pyttsx3 init failed: %s", exc)
            self._engine = None

    def say(self, text: str) -> None:
        """Speak *text* aloud and print to console."""
        if not text:
            return
        print(f"\n🧠 Turing: {text}\n")

        if self._engine is None:
            self._init_engine()

        if self._engine is not None:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
                self._engine.stop()
                return
            except Exception as exc:
                logger.warning("pyttsx3 speak failed: %s", exc)

        # Fallback: PowerShell on Windows
        if os.name == "nt":
            try:
                safe = text.replace("'", "`'")
                os.system(
                    f'PowerShell -Command "Add-Type –AssemblyName System.Speech; '
                    f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{safe}\')"'
                )
            except Exception as exc:
                logger.warning("PowerShell TTS failed: %s", exc)
