"""Inter-agent communication protocol — MIDI events + t-minus + conservation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    NOTE = "note"
    CONTROL = "control"
    PREDICTION = "prediction"
    CONSERVATION = "conservation"
    TEMPO = "tempo"
    LAYOUT = "layout"


@dataclass
class BandMessage:
    """Message between band agents.

    Carries MIDI event data, t-minus timestamps, and conservation metadata.
    """
    sender: str
    recipient: str  # agent ID or "broadcast"
    msg_type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    t_minus: float = 0.0           # seconds until event
    gamma: float = 0.0             # sender's spectral energy
    H: float = 0.0                 # sender's harmonic entropy
    C: float = 1.0                 # sender's conservation constant
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type.value,
            "payload": self.payload,
            "t_minus": self.t_minus,
            "gamma": self.gamma,
            "H": self.H,
            "C": self.C,
            "timestamp": self.timestamp,
        })

    @classmethod
    def from_json(cls, data: str) -> BandMessage:
        d = json.loads(data)
        return cls(
            sender=d["sender"],
            recipient=d["recipient"],
            msg_type=MessageType(d["msg_type"]),
            payload=d.get("payload", {}),
            t_minus=d.get("t_minus", 0.0),
            gamma=d.get("gamma", 0.0),
            H=d.get("H", 0.0),
            C=d.get("C", 1.0),
            timestamp=d.get("timestamp", time.time()),
        )

    def is_broadcast(self) -> bool:
        return self.recipient == "broadcast"

    def conservation_valid(self) -> bool:
        """Check if conservation law γ + H ≈ C holds."""
        return abs((self.gamma + self.H) - self.C) < 0.01
