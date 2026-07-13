"""Monitoring state and deterministic prediction domain tests."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from nextfight.infrastructure.database.entities import FightStatus
from nextfight.modules.monitoring.domain.prediction import predict_start
from nextfight.modules.monitoring.domain.state_machine import (
    FIGHT_TRANSITIONS,
    InvalidStateTransitionError,
    ensure_transition,
)


def test_fight_state_machine_accepts_valid_and_idempotent_transitions() -> None:
    """Allow policy transitions, same-state observations, and audited overrides."""
    ensure_transition(FightStatus.NEXT, FightStatus.WALKOUTS, FIGHT_TRANSITIONS)
    ensure_transition(FightStatus.LIVE, FightStatus.LIVE, FIGHT_TRANSITIONS)
    ensure_transition(
        FightStatus.COMPLETED,
        FightStatus.LIVE,
        FIGHT_TRANSITIONS,
        override=True,
    )


def test_fight_state_machine_rejects_invalid_transition() -> None:
    """Prevent a terminal fight from silently becoming live again."""
    with pytest.raises(InvalidStateTransitionError):
        ensure_transition(FightStatus.COMPLETED, FightStatus.LIVE, FIGHT_TRANSITIONS)


def test_prediction_is_transparent_and_degrades_with_uncertainty() -> None:
    """Produce a bounded window and lower confidence for degraded sources."""
    now = datetime.now(UTC)
    stable = predict_start(
        reference_at=now,
        fights_before=2,
        event_paused=False,
        provider_delayed=False,
    )
    degraded = predict_start(
        reference_at=now,
        fights_before=2,
        event_paused=True,
        provider_delayed=True,
    )
    assert stable.earliest_start_at < stable.predicted_start_at < stable.latest_start_at
    assert stable.confidence_score == Decimal("0.76")
    assert degraded.confidence_score < stable.confidence_score
    assert degraded.factors["provider_delayed"] is True
