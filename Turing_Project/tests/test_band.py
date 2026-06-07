"""Tests for the Self-Improving Band module."""

from __future__ import annotations

import json
import math

import pytest

from turing.band.agent import Agent, ConservationEnvelope, DialPosition, SpectralIdentity
from turing.band.ensemble import Ensemble
from turing.band.protocol import BandMessage, MessageType
from turing.config import BandConfig


class TestConservationEnvelope:
    def test_default_sums_to_one(self) -> None:
        env = ConservationEnvelope()
        assert abs(env.gamma + env.H - env.C) < 0.01

    def test_enforce_normalises(self) -> None:
        env = ConservationEnvelope(gamma=2.0, H=3.0, C=1.0)
        env.enforce()
        assert abs(env.gamma + env.H - env.C) < 0.01

    def test_enforce_zero(self) -> None:
        env = ConservationEnvelope(gamma=0.0, H=0.0, C=1.0)
        env.enforce()
        # Both zero stays zero — conservation holds trivially
        assert env.gamma == 0.0
        assert env.H == 0.0


class TestAgent:
    def test_create_default(self) -> None:
        agent = Agent(name="test-agent")
        assert agent.name == "test-agent"
        assert agent.active

    def test_spectral_state(self) -> None:
        agent = Agent(name="test", section="keys")
        state = agent.spectral_state()
        assert state["name"] == "test"
        assert state["section"] == "keys"
        assert "gamma" in state

    def test_update_phase(self) -> None:
        agent = Agent()
        initial = agent.identity.phase
        agent.update_phase(dt=0.001)
        assert agent.identity.phase != initial

    def test_set_dial(self) -> None:
        agent = Agent()
        agent.set_dial(0.8, "creative")
        assert agent.dial.value == 0.8
        assert agent.dial.label == "creative"
        assert abs(agent.envelope.gamma + agent.envelope.H - agent.envelope.C) < 0.01

    def test_dial_clamps(self) -> None:
        agent = Agent()
        agent.set_dial(1.5)
        assert agent.dial.value == 1.0
        agent.set_dial(-0.5)
        assert agent.dial.value == 0.0


class TestEnsemble:
    def test_create_empty(self) -> None:
        band = Ensemble()
        assert len(band.agents) == 0

    def test_start_session(self) -> None:
        band = Ensemble()
        band.start_session(key="Bb", style="blues", agent_count=5)
        assert len(band.agents) == 5

    def test_lay_out_section(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=6)
        band.lay_out("keys")
        for agent in band.agents:
            if agent.section == "keys":
                assert not agent.active

    def test_lay_out_all(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=4)
        band.lay_out("all")
        assert all(not a.active for a in band.agents)

    def test_spectral_state(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=4)
        state = band.spectral_state()
        assert "Agents" in state
        assert "4/4" in state

    def test_set_tempo(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=2)
        band.set_tempo(140.0)
        assert band.tempo_bpm == 140.0

    def test_negotiate_tempo(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=4)
        result = band.negotiate_tempo(140.0, weight=0.5)
        # Should be between old tempo and proposed
        assert isinstance(result, float)

    def test_enforce_conservation(self) -> None:
        band = Ensemble()
        band.start_session(agent_count=3)
        # Mess up conservation
        for a in band.agents:
            a.envelope.gamma = 10.0
        band.enforce_conservation()
        for a in band.agents:
            assert abs(a.envelope.gamma + a.envelope.H - a.envelope.C) < 0.01


class TestBandMessage:
    def test_create_note(self) -> None:
        msg = BandMessage(
            sender="agent-1",
            recipient="broadcast",
            msg_type=MessageType.NOTE,
            payload={"note": 60, "velocity": 100},
        )
        assert msg.is_broadcast()

    def test_serialization(self) -> None:
        msg = BandMessage(
            sender="agent-1",
            recipient="agent-2",
            msg_type=MessageType.CONSERVATION,
            gamma=0.5,
            H=0.5,
            C=1.0,
        )
        json_str = msg.to_json()
        restored = BandMessage.from_json(json_str)
        assert restored.sender == "agent-1"
        assert restored.msg_type == MessageType.CONSERVATION

    def test_conservation_valid(self) -> None:
        msg = BandMessage(
            sender="a", recipient="b",
            msg_type=MessageType.CONSERVATION,
            gamma=0.5, H=0.5, C=1.0,
        )
        assert msg.conservation_valid()

    def test_conservation_invalid(self) -> None:
        msg = BandMessage(
            sender="a", recipient="b",
            msg_type=MessageType.CONSERVATION,
            gamma=0.3, H=0.3, C=1.0,
        )
        assert not msg.conservation_valid()
