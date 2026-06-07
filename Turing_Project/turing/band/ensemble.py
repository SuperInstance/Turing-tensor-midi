"""Ensemble — collection of agents forming the band.

Tempo negotiation via Hodge decomposition.
Conservation law enforcement across agents.
"""

from __future__ import annotations

import logging
import math
from typing import Sequence

from .agent import Agent
from .tminus import TMinusClock
from ..config import BandConfig

logger = logging.getLogger(__name__)


class Ensemble:
    """A collection of agents = the Self-Improving Band."""

    def __init__(self, config: BandConfig | None = None) -> None:
        self.config = config or BandConfig()
        self.agents: list[Agent] = []
        self.tempo_bpm = self.config.tempo_bpm
        self._section_map: dict[str, list[Agent]] = {}

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)
        self._section_map.setdefault(agent.section, []).append(agent)

    def remove_agent(self, agent_id: str) -> None:
        self.agents = [a for a in self.agents if a.id != agent_id]
        self._rebuild_section_map()

    def _rebuild_section_map(self) -> None:
        self._section_map.clear()
        for a in self.agents:
            self._section_map.setdefault(a.section, []).append(a)

    def start_session(self, key: str = "C", style: str = "blues",
                      agent_count: int = 4) -> None:
        """Start a band session with *agent_count* agents."""
        self.agents.clear()
        self._section_map.clear()

        sections = ["bass", "drums", "keys", "guitar", "horns", "brass"]
        for i in range(agent_count):
            section = sections[i % len(sections)]
            agent = Agent(
                name=f"{section}-{i+1}",
                section=section,
            )
            self.add_agent(agent)

        logger.info("Session started: %s %s with %d agents", key, style, agent_count)

    def lay_out(self, section: str = "all") -> None:
        """Tell a section (or all) to lay out."""
        targets = self.agents if section == "all" else self._section_map.get(section, [])
        for agent in targets:
            agent.active = False
            agent.dial.set(0.0, "laying out")

    def spectral_state(self) -> str:
        """Return a human-readable spectral state summary."""
        active = sum(1 for a in self.agents if a.active)
        total = len(self.agents)
        avg_gamma = (
            sum(a.envelope.gamma for a in self.agents) / total if total else 0
        )
        avg_H = (
            sum(a.envelope.H for a in self.agents) / total if total else 0
        )
        return (
            f"Agents: {active}/{total} active. "
            f"Average spectral energy γ={avg_gamma:.3f}, "
            f"harmonic entropy H={avg_H:.3f}, "
            f"conservation C={avg_gamma + avg_H:.3f}. "
            f"Tempo: {self.tempo_bpm:.0f} BPM."
        )

    def set_tempo(self, bpm: float) -> None:
        """Set ensemble tempo via Hodge-style negotiation.

        Each agent's t-minus clock adjusts proportionally.
        """
        old = self.tempo_bpm
        self.tempo_bpm = bpm
        # Simple Hodge-inspired: agents converge via gradient
        ratio = bpm / old if old > 0 else 1.0
        for agent in self.agents:
            agent.identity.fundamental *= ratio

    def enforce_conservation(self) -> None:
        """Enforce γ + H = C across all agents."""
        for agent in self.agents:
            agent.envelope.enforce()

    def negotiate_tempo(self, proposed_bpm: float, weight: float = 0.5) -> float:
        """Hodge decomposition-inspired tempo negotiation.

        Each agent contributes a vote; result is a weighted average.
        """
        votes = []
        for agent in self.agents:
            # Agent votes based on its dial position and identity
            vote = proposed_bpm * (0.8 + 0.4 * agent.dial.value)
            votes.append(vote)

        if not votes:
            return proposed_bpm

        negotiated = (1 - weight) * proposed_bpm + weight * (sum(votes) / len(votes))
        self.set_tempo(negotiated)
        return negotiated
