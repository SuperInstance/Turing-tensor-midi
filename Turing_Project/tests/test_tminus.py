"""Tests for t-minus event timing."""

from __future__ import annotations

import math
import time
from unittest.mock import patch

import pytest

from turing.band.tminus import TMinusClock, PredictedEvent


class TestPredictedEvent:
    def test_t_minus_future(self) -> None:
        event = PredictedEvent(name="beat", predicted_time=time.time() + 10.0)
        assert event.t_minus > 9.0

    def test_t_minus_past(self) -> None:
        event = PredictedEvent(name="beat", predicted_time=time.time() - 5.0)
        assert event.t_minus == 0.0


class TestTMinusClock:
    def test_default_tempo(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0)
        assert clock.tempo_bpm == 120.0
        assert clock._beat_duration == 0.5

    def test_current_beat_wraps(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0, beats_per_bar=4)
        beat = clock.current_beat
        assert 0.0 <= beat < 4.0

    def test_current_phase_range(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0, beats_per_bar=4)
        phase = clock.current_phase
        assert 0.0 <= phase < 2 * math.pi

    def test_predict_next(self) -> None:
        clock = TMinusClock(tempo_bpm=60.0)  # 1 beat per second
        event = clock.predict_next("downbeat", beats_ahead=4.0)
        assert event.t_minus > 3.0
        assert event.t_minus < 5.0
        assert event.name == "downbeat"

    def test_due_events(self) -> None:
        clock = TMinusClock(tempo_bpm=60.0)
        # Predict an event in the past
        event = PredictedEvent(name="past", predicted_time=time.time() - 1.0)
        clock._predictions.append(event)
        due = clock.due_events()
        assert len(due) == 1
        assert due[0].name == "past"
        # Should be removed
        assert len(clock._predictions) == 0

    def test_update_tempo(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0)
        clock.update_tempo(60.0)
        assert clock.tempo_bpm == 60.0
        assert clock._beat_duration == 1.0

    def test_beat_phase_distance(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0, beats_per_bar=4)
        # Mock _origin so current_beat returns a known value
        elapsed_for_beat_1 = 1.0 * clock._beat_duration  # 0.5s for beat 1
        clock._origin = time.time() - elapsed_for_beat_1
        dist = clock.beat_phase_distance(3.0)
        assert abs(dist - 2.0) < 0.1

    def test_beat_phase_distance_wraps(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0, beats_per_bar=4)
        elapsed_for_beat_3 = 3.0 * clock._beat_duration  # 1.5s for beat 3
        clock._origin = time.time() - elapsed_for_beat_3
        dist = clock.beat_phase_distance(1.0)
        assert abs(dist - 2.0) < 0.1

    def test_phase_wrapping(self) -> None:
        clock = TMinusClock(tempo_bpm=120.0, beats_per_bar=4)
        event = clock.predict_next("test", beats_ahead=100.0)
        assert 0.0 <= event.phase < 2 * math.pi
