"""T-minus event timing — local countdown, no shared clock."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field


@dataclass
class PredictedEvent:
    """An event predicted by an agent's local t-minus clock."""
    name: str
    predicted_time: float     # absolute time (seconds since epoch)
    confidence: float = 1.0
    phase: float = 0.0        # cyclical phase [0, 2π)
    metadata: dict = field(default_factory=dict)

    @property
    def t_minus(self) -> float:
        """Seconds until this event."""
        return max(0.0, self.predicted_time - time.time())


class TMinusClock:
    """Local countdown clock — each agent maintains its own.

    No shared clock. Agents predict events independently based on
    local tempo perception and phase estimation.
    """

    def __init__(self, tempo_bpm: float = 120.0, beats_per_bar: int = 4) -> None:
        self.tempo_bpm = tempo_bpm
        self.beats_per_bar = beats_per_bar
        self._beat_duration = 60.0 / tempo_bpm
        self._bar_duration = self._beat_duration * beats_per_bar
        self._origin = time.time()
        self._predictions: list[PredictedEvent] = []

    @property
    def current_beat(self) -> float:
        """Current beat position within the bar (0-based)."""
        elapsed = time.time() - self._origin
        return (elapsed / self._beat_duration) % self.beats_per_bar

    @property
    def current_phase(self) -> float:
        """Current phase in [0, 2π)."""
        return (self.current_beat / self.beats_per_bar) * 2 * math.pi

    def predict_next(self, event_name: str, beats_ahead: float = 1.0,
                     confidence: float = 1.0) -> PredictedEvent:
        """Predict the next occurrence of an event."""
        now = time.time()
        predicted_time = now + (beats_ahead * self._beat_duration)
        phase = ((self.current_beat + beats_ahead) / self.beats_per_bar) * 2 * math.pi
        phase %= (2 * math.pi)

        event = PredictedEvent(
            name=event_name,
            predicted_time=predicted_time,
            confidence=confidence,
            phase=phase,
        )
        self._predictions.append(event)
        return event

    def due_events(self) -> list[PredictedEvent]:
        """Return events that are due (t_minus ≈ 0)."""
        now = time.time()
        due = [e for e in self._predictions if e.predicted_time <= now]
        self._predictions = [e for e in self._predictions if e.predicted_time > now]
        return due

    def update_tempo(self, new_bpm: float) -> None:
        """Update tempo and recalculate durations."""
        self.tempo_bpm = new_bpm
        self._beat_duration = 60.0 / new_bpm
        self._bar_duration = self._beat_duration * self.beats_per_bar

    def beat_phase_distance(self, target_beat: float) -> float:
        """Distance in beats to a target beat position, wrapping."""
        diff = (target_beat - self.current_beat) % self.beats_per_bar
        return diff
