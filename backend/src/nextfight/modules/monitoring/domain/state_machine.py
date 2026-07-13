"""Explicit event and fight lifecycle transition policies."""

from collections.abc import Mapping

from nextfight.infrastructure.database.entities import EventStatus, FightStatus

EVENT_TRANSITIONS: Mapping[EventStatus, frozenset[EventStatus]] = {
    EventStatus.SCHEDULED: frozenset(
        {EventStatus.DELAYED, EventStatus.LIVE, EventStatus.CANCELLED}
    ),
    EventStatus.DELAYED: frozenset(
        {EventStatus.SCHEDULED, EventStatus.LIVE, EventStatus.CANCELLED}
    ),
    EventStatus.LIVE: frozenset(
        {EventStatus.PAUSED, EventStatus.COMPLETED, EventStatus.CANCELLED}
    ),
    EventStatus.PAUSED: frozenset(
        {EventStatus.LIVE, EventStatus.COMPLETED, EventStatus.CANCELLED}
    ),
    EventStatus.COMPLETED: frozenset(),
    EventStatus.CANCELLED: frozenset(),
}

FIGHT_TRANSITIONS: Mapping[FightStatus, frozenset[FightStatus]] = {
    FightStatus.SCHEDULED: frozenset({FightStatus.NEXT, FightStatus.CANCELLED}),
    FightStatus.NEXT: frozenset(
        {FightStatus.WALKOUTS, FightStatus.LIVE, FightStatus.CANCELLED}
    ),
    FightStatus.WALKOUTS: frozenset({FightStatus.LIVE, FightStatus.CANCELLED}),
    FightStatus.LIVE: frozenset(
        {
            FightStatus.PAUSED,
            FightStatus.COMPLETED,
            FightStatus.NO_CONTEST,
        }
    ),
    FightStatus.PAUSED: frozenset(
        {
            FightStatus.LIVE,
            FightStatus.COMPLETED,
            FightStatus.NO_CONTEST,
        }
    ),
    FightStatus.COMPLETED: frozenset(),
    FightStatus.CANCELLED: frozenset(),
    FightStatus.NO_CONTEST: frozenset(),
}


class InvalidStateTransitionError(ValueError):
    """Raised when a lifecycle transition violates domain policy."""


def ensure_transition[Status: (EventStatus, FightStatus)](
    current: Status,
    target: Status,
    policy: Mapping[Status, frozenset[Status]],
    *,
    override: bool = False,
) -> None:
    """Validate a transition, permitting no-op idempotency and explicit override."""
    if current == target or override:
        return
    if target not in policy[current]:
        message = f"Invalid transition from {current.value} to {target.value}."
        raise InvalidStateTransitionError(message)
