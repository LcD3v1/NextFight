"""Hybrid fight-state ingestion and prediction orchestration."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Event,
    EventStatus,
    Fight,
    FightStateEvent,
    FightStatus,
    OutboxEvent,
    Prediction,
)
from nextfight.modules.monitoring.domain.prediction import predict_start
from nextfight.modules.monitoring.domain.state_machine import (
    FIGHT_TRANSITIONS,
    ensure_transition,
)


class MonitoringNotFoundError(LookupError):
    """Raised when a monitored aggregate does not exist."""


class ManualOverrideActiveError(ValueError):
    """Raised when provider input conflicts with a recent manual correction."""


class MonitoringService:
    """Apply idempotent observations and persist their downstream effects."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        """Bind monitoring to one atomic database transaction."""
        self._session = session
        self._settings = settings

    async def apply_fight_state(  # noqa: PLR0913
        self,
        *,
        fight_id: UUID,
        target: FightStatus,
        source: str,
        idempotency_key: str,
        occurred_at: datetime,
        round_number: int | None = None,
        clock_seconds: int | None = None,
        payload: dict[str, Any] | None = None,
        override: bool = False,
    ) -> FightStateEvent:
        """Apply one external or manual state observation exactly once."""
        existing = await self._session.scalar(
            select(FightStateEvent).where(
                FightStateEvent.idempotency_key == idempotency_key
            )
        )
        if existing is not None:
            return existing
        fight = await self._session.scalar(
            select(Fight).where(Fight.id == fight_id).with_for_update()
        )
        if fight is None:
            raise MonitoringNotFoundError
        self._enforce_source_priority(fight, source, occurred_at)
        ensure_transition(fight.status, target, FIGHT_TRANSITIONS, override=override)
        fight.status = target
        fight.version += 1
        if target == FightStatus.LIVE and fight.actual_start_at is None:
            fight.actual_start_at = occurred_at
        if target in {
            FightStatus.COMPLETED,
            FightStatus.CANCELLED,
            FightStatus.NO_CONTEST,
        }:
            fight.actual_end_at = occurred_at
        if source == "manual":
            provider_payload = dict(fight.provider_payload)
            provider_payload["manual_override_until"] = (
                occurred_at + timedelta(minutes=self._settings.manual_override_minutes)
            ).isoformat()
            fight.provider_payload = provider_payload
        observation = FightStateEvent(
            fight_id=fight.id,
            event_id=fight.event_id,
            state=target,
            round_number=round_number,
            clock_seconds=clock_seconds,
            source=source,
            idempotency_key=idempotency_key,
            payload=payload or {},
            occurred_at=occurred_at,
        )
        self._session.add(observation)
        await self._advance_card(fight)
        await self._recalculate_predictions(fight.event_id, occurred_at)
        self._session.add(
            OutboxEvent(
                topic=f"fight:{fight.id}",
                event_type=f"fight.{target.value}",
                idempotency_key=f"realtime:{idempotency_key}",
                payload={
                    "fight_id": str(fight.id),
                    "event_id": str(fight.event_id),
                    "status": target.value,
                    "occurred_at": occurred_at.isoformat(),
                },
                status="pending",
                attempts=0,
                available_at=datetime.now(UTC),
            )
        )
        await self._session.flush()
        return observation

    async def latest_prediction(self, fight_id: UUID) -> Prediction:
        """Return the latest deterministic prediction for a fight."""
        prediction = await self._session.scalar(
            select(Prediction)
            .where(Prediction.fight_id == fight_id)
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .limit(1)
        )
        if prediction is None:
            raise MonitoringNotFoundError
        return prediction

    async def timeline(self, event_id: UUID) -> list[FightStateEvent]:
        """Return the immutable observed state timeline for an event."""
        if await self._session.get(Event, event_id) is None:
            raise MonitoringNotFoundError
        return list(
            await self._session.scalars(
                select(FightStateEvent)
                .where(FightStateEvent.event_id == event_id)
                .order_by(FightStateEvent.occurred_at, FightStateEvent.id)
            )
        )

    async def _advance_card(self, current: Fight) -> None:
        if current.status not in {
            FightStatus.COMPLETED,
            FightStatus.CANCELLED,
            FightStatus.NO_CONTEST,
        }:
            return
        upcoming = await self._session.scalar(
            select(Fight)
            .where(
                Fight.event_id == current.event_id,
                Fight.current_order > current.current_order,
                Fight.status == FightStatus.SCHEDULED,
            )
            .order_by(Fight.current_order)
            .with_for_update()
            .limit(1)
        )
        if upcoming is not None:
            upcoming.status = FightStatus.NEXT
            upcoming.version += 1

    async def _recalculate_predictions(
        self, event_id: UUID, reference_at: datetime
    ) -> None:
        event = await self._session.get(Event, event_id)
        if event is None:
            raise MonitoringNotFoundError
        fights = list(
            await self._session.scalars(
                select(Fight)
                .where(Fight.event_id == event_id)
                .order_by(Fight.current_order)
            )
        )
        pending = {
            FightStatus.SCHEDULED,
            FightStatus.NEXT,
            FightStatus.WALKOUTS,
        }
        for index, fight in enumerate(fights):
            if fight.status not in pending:
                continue
            fights_before = sum(
                candidate.status
                not in {
                    FightStatus.COMPLETED,
                    FightStatus.CANCELLED,
                    FightStatus.NO_CONTEST,
                }
                for candidate in fights[:index]
            )
            result = predict_start(
                reference_at=reference_at,
                fights_before=fights_before,
                event_paused=event.status == EventStatus.PAUSED,
                provider_delayed=bool(event.provider_payload.get("provider_delayed")),
            )
            self._session.add(
                Prediction(
                    fight_id=fight.id,
                    predicted_start_at=result.predicted_start_at,
                    earliest_start_at=result.earliest_start_at,
                    latest_start_at=result.latest_start_at,
                    confidence_score=result.confidence_score,
                    model_version=result.model_version,
                    factors=result.factors,
                )
            )

    @staticmethod
    def _enforce_source_priority(
        fight: Fight, source: str, occurred_at: datetime
    ) -> None:
        marker = fight.provider_payload.get("manual_override_until")
        if source != "provider" or not isinstance(marker, str):
            return
        try:
            protected_until = datetime.fromisoformat(marker)
        except ValueError:
            return
        if occurred_at < protected_until:
            raise ManualOverrideActiveError
