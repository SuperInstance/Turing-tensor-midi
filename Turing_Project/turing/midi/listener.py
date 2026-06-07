"""MIDI input listener — convert MIDI events to voice commands."""

from __future__ import annotations

import logging
from typing import Callable

logger = logging.getLogger(__name__)

# Optional: midi dependency
try:
    import mido
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False


class MidiListener:
    """Listen for MIDI input and translate to voice commands.

    Requires ``mido`` and a MIDI input port.
    """

    def __init__(self, port_name: str | None = None,
                 on_event: Callable[[dict], None] | None = None) -> None:
        if not HAS_MIDO:
            logger.warning("mido not installed — MIDI listener disabled")
            self._enabled = False
            return
        self._enabled = True
        self._port_name = port_name
        self._on_event = on_event
        self._running = False

    def start(self) -> None:
        if not self._enabled:
            return
        self._running = True
        try:
            with mido.open_input(self._port_name) as port:
                logger.info("MIDI input opened: %s", port.name)
                for msg in port:
                    if not self._running:
                        break
                    if msg.type in ("note_on", "note_off", "control_change"):
                        event = self._parse(msg)
                        if self._on_event:
                            self._on_event(event)
        except Exception as exc:
            logger.error("MIDI listener error: %s", exc)

    def stop(self) -> None:
        self._running = False

    @staticmethod
    def _parse(msg: "mido.Message") -> dict:
        """Convert a MIDI message to a dict."""
        return {
            "type": msg.type,
            "note": getattr(msg, "note", 0),
            "velocity": getattr(msg, "velocity", 0),
            "control": getattr(msg, "control", 0),
            "value": getattr(msg, "value", 0),
            "channel": getattr(msg, "channel", 0),
            "time": msg.time,
        }
