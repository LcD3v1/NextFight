"""Audited administrative mutation and operational query use cases."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Alert,
    AlertDelivery,
    Athlete,
    AuditLog,
    Device,
    Event,
    EventChange,
    EventStatus,
    Fight,
    FightStatus,
    Organization,
    User,
)
from nextfight.infrastructure.database.models import EntityMixin
from nextfight.modules.admin.api.schemas import (
    AlertDispatchCommand,
    AthleteCreate,
    DashboardResponse,
    EventCreate,
    EventStateCommand,
    EventUpdate,
    FightCreate,
    FightStateCommand,
    FightUpdate,
    OrganizationCreate,
)
from nextfight.modules.monitoring.application.service import MonitoringService
from nextfight.modules.monitoring.domain.state_machine import (
    EVENT_TRANSITIONS,
    ensure_transition,
)


class AdminNotFoundError(LookupError):
    """Raised when an administrative target does not exist."""


class InvalidCardOrderError(ValueError):
    """Raised when a card order is incomplete or contains foreign fights."""


class AdminService:
    """Coordinate privileged mutations and mandatory audit logging."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        actor: User,
        ip_address: str | None,
    ) -> None:
        """Bind operations to one authenticated actor and transaction."""
        self._session = session
        self._settings = settings
        self._actor = actor
        self._ip_address = ip_address

    async def create_organization(self, payload: OrganizationCreate) -> Organization:
        """Create and audit an organization."""
        entity = Organization(**payload.model_dump(), active=True)
        self._session.add(entity)
        await self._session.flush()
        self._audit(
            "organization.created",
            "organization",
            entity.id,
            payload.model_dump(mode="json"),
        )
        return entity

    async def create_athlete(self, payload: AthleteCreate) -> Athlete:
        """Create and audit an athlete."""
        entity = Athlete(**payload.model_dump(), external_ids={})
        self._session.add(entity)
        await self._session.flush()
        self._audit(
            "athlete.created", "athlete", entity.id, payload.model_dump(mode="json")
        )
        return entity

    async def create_event(self, payload: EventCreate) -> Event:
        """Create a scheduled event for an existing organization."""
        if await self._session.get(Organization, payload.organization_id) is None:
            raise AdminNotFoundError
        entity = Event(
            **payload.model_dump(),
            status=EventStatus.SCHEDULED,
            provider_payload={},
            version=1,
        )
        self._session.add(entity)
        await self._session.flush()
        self._audit(
            "event.created", "event", entity.id, payload.model_dump(mode="json")
        )
        return entity

    async def update_event(self, event_id: UUID, payload: EventUpdate) -> Event:
        """Patch and audit mutable event metadata."""
        event = await self._locked(Event, event_id)
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(event, field, value)
        event.version += 1
        self._audit("event.updated", "event", event.id, _json_safe(changes))
        return event

    async def create_fight(self, payload: FightCreate) -> Fight:
        """Add and audit a fight whose references all exist."""
        if await self._session.get(Event, payload.event_id) is None:
            raise AdminNotFoundError
        for athlete_id in (payload.red_athlete_id, payload.blue_athlete_id):
            if await self._session.get(Athlete, athlete_id) is None:
                raise AdminNotFoundError
        entity = Fight(
            **payload.model_dump(),
            scheduled_order=payload.current_order,
            status=FightStatus.SCHEDULED,
            provider_payload={},
            version=1,
        )
        self._session.add(entity)
        await self._session.flush()
        self._audit(
            "fight.created", "fight", entity.id, payload.model_dump(mode="json")
        )
        return entity

    async def update_fight(self, fight_id: UUID, payload: FightUpdate) -> Fight:
        """Patch and audit fight metadata."""
        fight = await self._locked(Fight, fight_id)
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(fight, field, value)
        fight.version += 1
        self._audit("fight.updated", "fight", fight.id, _json_safe(changes))
        return fight

    async def apply_fight_state(
        self, fight_id: UUID, payload: FightStateCommand
    ) -> UUID:
        """Apply a manual monitoring observation and audit the command."""
        observation = await MonitoringService(
            self._session, self._settings
        ).apply_fight_state(
            fight_id=fight_id,
            target=payload.state,
            source="manual",
            idempotency_key=payload.idempotency_key,
            occurred_at=payload.occurred_at,
            round_number=payload.round_number,
            clock_seconds=payload.clock_seconds,
            override=payload.override,
        )
        self._audit(
            "fight.state_changed",
            "fight",
            fight_id,
            payload.model_dump(mode="json"),
        )
        return observation.id

    async def apply_event_state(
        self, event_id: UUID, payload: EventStateCommand
    ) -> Event:
        """Apply and audit an event lifecycle transition."""
        event = await self._locked(Event, event_id)
        before = event.status
        ensure_transition(
            before, payload.state, EVENT_TRANSITIONS, override=payload.override
        )
        event.status = payload.state
        event.version += 1
        if payload.state == EventStatus.LIVE and event.actual_start_at is None:
            event.actual_start_at = datetime.now(UTC)
        self._session.add(
            EventChange(
                event_id=event.id,
                entity_type="event",
                entity_id=event.id,
                action="state_changed",
                before_data={"status": before.value},
                after_data={"status": payload.state.value},
                source="manual",
                actor_user_id=self._actor.id,
            )
        )
        self._audit(
            "event.state_changed", "event", event.id, payload.model_dump(mode="json")
        )
        return event

    async def reorder_card(self, event_id: UUID, fight_ids: list[UUID]) -> None:
        """Atomically replace card order and retain its previous ordering."""
        fights = list(
            await self._session.scalars(
                select(Fight)
                .where(Fight.event_id == event_id)
                .order_by(Fight.current_order)
                .with_for_update()
            )
        )
        if (
            not fights
            or len(fight_ids) != len(set(fight_ids))
            or {fight.id for fight in fights} != set(fight_ids)
        ):
            raise InvalidCardOrderError
        before = [str(fight.id) for fight in fights]
        by_id = {fight.id: fight for fight in fights}
        for index, fight in enumerate(fights, start=1):
            fight.current_order = -index
        await self._session.flush()
        for index, fight_id in enumerate(fight_ids, start=1):
            by_id[fight_id].current_order = index
            by_id[fight_id].version += 1
        self._session.add(
            EventChange(
                event_id=event_id,
                entity_type="card",
                entity_id=event_id,
                action="reordered",
                before_data={"fight_ids": before},
                after_data={"fight_ids": [str(item) for item in fight_ids]},
                source="manual",
                actor_user_id=self._actor.id,
            )
        )
        self._audit(
            "card.reordered",
            "event",
            event_id,
            {"fight_ids": [str(item) for item in fight_ids]},
        )

    async def dashboard(self) -> DashboardResponse:
        """Return current operational counters."""
        return DashboardResponse(
            live_events=int(
                await self._session.scalar(
                    select(func.count())
                    .select_from(Event)
                    .where(Event.status == EventStatus.LIVE)
                )
                or 0
            ),
            active_users=int(
                await self._session.scalar(
                    select(func.count())
                    .select_from(User)
                    .where(User.status == "active")
                )
                or 0
            ),
            pending_deliveries=int(
                await self._session.scalar(
                    select(func.count())
                    .select_from(AlertDelivery)
                    .where(AlertDelivery.status == "pending")
                )
                or 0
            ),
            failed_deliveries=int(
                await self._session.scalar(
                    select(func.count())
                    .select_from(AlertDelivery)
                    .where(AlertDelivery.status == "failed")
                )
                or 0
            ),
        )

    async def audit_logs(self, limit: int) -> list[AuditLog]:
        """Return newest immutable privileged operations."""
        return list(
            await self._session.scalars(
                select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
            )
        )

    async def organizations(self, limit: int) -> list[Organization]:
        """Return organizations for event management forms."""
        return list(
            await self._session.scalars(
                select(Organization).order_by(Organization.name).limit(limit)
            )
        )

    async def athletes(self, limit: int) -> list[Athlete]:
        """Return athletes for card management forms."""
        return list(
            await self._session.scalars(
                select(Athlete).order_by(Athlete.name).limit(limit)
            )
        )

    async def users(self, limit: int) -> list[User]:
        """Return privacy-limited user operations data."""
        return list(
            await self._session.scalars(
                select(User).order_by(User.created_at.desc()).limit(limit)
            )
        )

    async def deliveries(self, limit: int) -> list[AlertDelivery]:
        """Return latest push delivery outcomes for diagnostics."""
        return list(
            await self._session.scalars(
                select(AlertDelivery)
                .order_by(AlertDelivery.created_at.desc())
                .limit(limit)
            )
        )

    async def dispatch_alert(self, payload: AlertDispatchCommand) -> int:
        """Queue one audited manual alert for every enabled owned device."""
        alert = await self._session.get(Alert, payload.alert_id)
        if alert is None:
            raise AdminNotFoundError
        device_ids = list(
            await self._session.scalars(
                select(Device.id).where(
                    Device.user_id == alert.user_id,
                    Device.notifications_enabled.is_(True),
                )
            )
        )
        now = datetime.now(UTC)
        queued = 0
        for device_id in device_ids:
            statement = (
                insert(AlertDelivery)
                .values(
                    alert_id=alert.id,
                    device_id=device_id,
                    channel="push",
                    idempotency_key=(f"admin:{payload.idempotency_key}:{device_id}"),
                    status="pending",
                    title=payload.title,
                    body=payload.body,
                    data={
                        "type": "admin.alert",
                        "fight_id": str(alert.fight_id),
                    },
                    attempts=0,
                    next_attempt_at=now,
                )
                .on_conflict_do_nothing(index_elements=["idempotency_key"])
                .returning(AlertDelivery.id)
            )
            if await self._session.scalar(statement) is not None:
                queued += 1
        self._audit(
            "alert.dispatched",
            "alert",
            alert.id,
            {
                "idempotency_key": payload.idempotency_key,
                "queued": queued,
            },
        )
        return queued

    async def _locked[Entity: EntityMixin](
        self, entity_type: type[Entity], entity_id: UUID
    ) -> Entity:
        entity = await self._session.scalar(
            select(entity_type).where(entity_type.id == entity_id).with_for_update()
        )
        if entity is None:
            raise AdminNotFoundError
        return entity

    def _audit(
        self, action: str, entity_type: str, entity_id: UUID, changes: dict[str, Any]
    ) -> None:
        self._session.add(
            AuditLog(
                actor_user_id=self._actor.id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                ip_address=self._ip_address,
                changes=changes,
            )
        )


def _json_safe(changes: dict[str, Any]) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, (UUID, datetime)) else value
        for key, value in changes.items()
    }
