"""Tensor map — MIDI → tensor operation mappings.

velocity  → tensor weight
pitch class → harmonic dimension
rhythm → temporal kernel
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class TensorEvent:
    """A MIDI event mapped to tensor space."""

    weight: float          # normalised velocity [0, 1]
    dimension: int         # pitch class (0–11)
    temporal: float        # normalised temporal position [0, 1]
    channel: int           # MIDI channel
    raw_note: int          # original MIDI note
    raw_velocity: int      # original MIDI velocity


class TensorMap:
    """Map MIDI events into tensor representations."""

    def __init__(self, tempo_bpm: float = 120.0, beats_per_bar: int = 4) -> None:
        self.tempo_bpm = tempo_bpm
        self.beats_per_bar = beats_per_bar
        self._beat_duration = 60.0 / tempo_bpm

    def midi_to_tensor(self, note: int, velocity: int, channel: int = 0,
                       beat_position: float = 0.0) -> TensorEvent:
        """Convert a MIDI note event to a tensor representation."""
        weight = self._normalise_velocity(velocity)
        dimension = note % 12
        temporal = self._normalise_temporal(beat_position)
        return TensorEvent(
            weight=weight,
            dimension=dimension,
            temporal=temporal,
            channel=channel,
            raw_note=note,
            raw_velocity=velocity,
        )

    @staticmethod
    def _normalise_velocity(velocity: int) -> float:
        """Normalise MIDI velocity (0–127) to [0, 1]."""
        return max(0.0, min(velocity / 127.0, 1.0))

    def _normalise_temporal(self, beat_position: float) -> float:
        """Normalise a beat position to [0, 1] within a bar."""
        bar_length = self.beats_per_bar
        return (beat_position % bar_length) / bar_length

    def pitch_class_name(self, note: int) -> str:
        """Return pitch class name for a MIDI note."""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return names[note % 12]

    def tensor_to_midi(self, event: TensorEvent) -> dict:
        """Reverse: tensor event → MIDI parameters."""
        return {
            "note": event.raw_note,
            "velocity": int(event.weight * 127),
            "channel": event.channel,
            "beat_position": event.temporal * self.beats_per_bar,
        }

    def compute_harmonic_vector(self, events: list[TensorEvent]) -> list[float]:
        """Compute a 12-dimensional harmonic vector from tensor events."""
        vector = [0.0] * 12
        for event in events:
            vector[event.dimension] += event.weight
        # Normalise
        total = sum(vector)
        if total > 0:
            vector = [v / total for v in vector]
        return vector
