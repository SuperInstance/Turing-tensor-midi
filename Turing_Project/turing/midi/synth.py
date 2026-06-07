"""MIDI output synth — band agents to MIDI notes."""

from __future__ import annotations

import logging
from typing import Sequence

logger = logging.getLogger(__name__)

try:
    import mido
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False


class MidiSynth:
    """Synthesize MIDI output from band agent decisions."""

    def __init__(self, port_name: str | None = None) -> None:
        if not HAS_MIDO:
            logger.warning("mido not installed — MIDI synth disabled")
            self._enabled = False
            return
        self._enabled = True
        self._port_name = port_name
        self._port = None

    def open(self) -> None:
        if not self._enabled:
            return
        self._port = mido.open_output(self._port_name)

    def close(self) -> None:
        if self._port:
            self._port.close()
            self._port = None

    def play_note(self, note: int, velocity: int = 100,
                  channel: int = 0, duration: float = 0.5) -> None:
        """Send a note_on / note_off pair."""
        if not self._port:
            return
        self._port.send(mido.Message("note_on", note=note,
                                     velocity=velocity, channel=channel))
        # Duration scheduling would need a clock; simplified here
        self._port.send(mido.Message("note_off", note=note,
                                     velocity=0, channel=channel))

    def play_chord(self, notes: Sequence[int], velocity: int = 90,
                   channel: int = 0) -> None:
        """Play multiple notes simultaneously."""
        for note in notes:
            self.play_note(note, velocity, channel)

    def control_change(self, control: int, value: int,
                       channel: int = 0) -> None:
        if self._port:
            self._port.send(mido.Message("control_change",
                                         control=control, value=value,
                                         channel=channel))
