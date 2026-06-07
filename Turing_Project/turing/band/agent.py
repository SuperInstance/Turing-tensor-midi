"""Single band agent — spectral identity with conservation envelope."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field


@dataclass
class SpectralIdentity:
    """An agent's unique spectral fingerprint."""
    fundamental: float = 440.0   # Hz
    harmonics: list[float] = field(default_factory=lambda: [1.0, 0.5, 0.25])
    phase: float = 0.0           # radians
    dimension: int = 0           # harmonic dimension (pitch class)


@dataclass
class ConservationEnvelope:
    """γ + H = C conservation law for agent energy."""
    gamma: float = 0.5           # spectral energy
    H: float = 0.5               # harmonic entropy
    C: float = 1.0               # constant total

    def enforce(self) -> None:
        """Re-normalise to satisfy γ + H = C."""
        total = self.gamma + self.H
        if total > 0:
            scale = self.C / total
            self.gamma *= scale
            self.H *= scale


@dataclass
class DialPosition:
    """Agent's current creative dial position [0, 1]."""
    value: float = 0.5
    label: str = "neutral"

    def set(self, value: float, label: str = "") -> None:
        self.value = max(0.0, min(1.0, value))
        self.label = label or self.label


class Agent:
    """A single Self-Improving Band agent."""

    def __init__(self, name: str = "", identity: SpectralIdentity | None = None,
                 section: str = "keys") -> None:
        self.id = str(uuid.uuid4())[:8]
        self.name = name or f"agent-{self.id}"
        self.identity = identity or SpectralIdentity()
        self.envelope = ConservationEnvelope()
        self.dial = DialPosition()
        self.section = section
        self.active = True

    def spectral_state(self) -> dict:
        """Return current spectral state as a dict."""
        return {
            "id": self.id,
            "name": self.name,
            "section": self.section,
            "fundamental_hz": self.identity.fundamental,
            "dimension": self.identity.dimension,
            "phase": self.identity.phase,
            "gamma": self.envelope.gamma,
            "H": self.envelope.H,
            "C": self.envelope.C,
            "dial": self.dial.value,
            "dial_label": self.dial.label,
            "active": self.active,
        }

    def update_phase(self, dt: float) -> None:
        """Advance phase by *dt* seconds at fundamental frequency."""
        self.identity.phase += 2 * math.pi * self.identity.fundamental * dt
        self.identity.phase %= (2 * math.pi)

    def set_dial(self, value: float, label: str = "") -> None:
        """Set creative dial and update conservation envelope."""
        self.dial.set(value, label)
        self.envelope.gamma = value
        self.envelope.H = self.envelope.C - value
        self.envelope.enforce()

    def __repr__(self) -> str:
        return f"Agent({self.name!r}, section={self.section!r})"
