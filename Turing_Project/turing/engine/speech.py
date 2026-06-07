"""SpeechRecognition wrapper — microphone input to text."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import speech_recognition as sr

logger = logging.getLogger(__name__)


@dataclass
class SpeechResult:
    text: str
    confidence: float = 0.0


class SpeechEngine:
    """Thin wrapper around ``speech_recognition`` with configurable params."""

    def __init__(self, language: str = "en-GB", timeout: int = 8,
                 phrase_limit: int = 10) -> None:
        self._recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        self.phrase_limit = phrase_limit

    def listen(self, ambient_calibrate: bool = True) -> SpeechResult:
        """Capture audio from the default microphone and transcribe."""
        with sr.Microphone() as source:
            if ambient_calibrate:
                self._recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self._recognizer.listen(
                    source, timeout=self.timeout,
                    phrase_time_limit=self.phrase_limit,
                )
                text = self._recognizer.recognize_google(
                    audio, language=self.language,
                )
                return SpeechResult(text=text.lower(), confidence=1.0)
            except sr.UnknownValueError:
                return SpeechResult(text="")
            except sr.RequestError as exc:
                logger.error("Network issue: %s", exc)
                return SpeechResult(text="")

    def listen_raw(self) -> sr.AudioData | None:
        """Return raw AudioData for custom processing."""
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source)
            try:
                return self._recognizer.listen(
                    source, timeout=self.timeout,
                    phrase_time_limit=self.phrase_limit,
                )
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
