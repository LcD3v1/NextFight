"""Hybrid monitoring integration tests against real infrastructure."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Alert,
    AlertDelivery,
    Athlete,
    Device,
    Event,
    EventStatus,
    Fight,
    FightStateEvent,
    FightStatus,
    Organization,
    OutboxEvent,
    Prediction,
    User,
)
from nextfight.infrastructure.database.session import create_database_engine
from nextfight.modules.monitoring.application.service import (
    ManualOverrideActiveError,
    MonitoringService,
)
from nextfight.modules.monitoring.domain.state_machine import (
    InvalidStateTransitionError,
)


@pytest.mark.integration
async def test_hybrid_state_prediction_timeline_and_idempotency(
    client: httpx.AsyncClient,
    settings: Settings,
) -> None:
    """Apply manual state, advance card, predict, and reject stale provider input."""
    engine = create_database_engine(settings)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        event_id, first_id, second_id, user_id = await _seed_card(session)
    occurred_at = datetime.now(UTC)
    key = f"manual:{uuid4()}"
    try:
        async with factory.begin() as session:
            service = MonitoringService(session, settings)
            observation = await service.apply_fight_state(
                fight_id=first_id,
                target=FightStatus.COMPLETED,
                source="manual",
                idempotency_key=key,
                occurred_at=occurred_at,
                override=True,
            )
            duplicate = await service.apply_fight_state(
                fight_id=first_id,
                target=FightStatus.COMPLETED,
                source="manual",
                idempotency_key=key,
                occurred_at=occurred_at,
                override=True,
            )
            assert duplicate.id == observation.id

        async with factory() as session:
            next_fight = await session.get(Fight, second_id)
            assert next_fight is not None
            assert next_fight.status == FightStatus.NEXT
            assert await session.scalar(
                select(OutboxEvent).where(
                    OutboxEvent.idempotency_key == f"realtime:{key}"
                )
            )
            delivery = await session.scalar(
                select(AlertDelivery)
                .join(Alert, Alert.id == AlertDelivery.alert_id)
                .where(Alert.fight_id == second_id)
            )
            assert delivery is not None
            assert delivery.title == "Sua luta é a próxima"
            assert delivery.data["fight_id"] == str(second_id)

        timeline = await client.get(f"/api/v1/events/{event_id}/timeline")
        assert timeline.status_code == HTTPStatus.OK
        assert timeline.json()[0]["state"] == "completed"
        prediction = await client.get(f"/api/v1/fights/{second_id}/prediction")
        assert prediction.status_code == HTTPStatus.OK
        assert prediction.json()["model_version"] == "rules-v1"

        async with factory.begin() as session:
            with pytest.raises(ManualOverrideActiveError):
                await MonitoringService(session, settings).apply_fight_state(
                    fight_id=first_id,
                    target=FightStatus.LIVE,
                    source="provider",
                    idempotency_key=f"provider:{uuid4()}",
                    occurred_at=occurred_at + timedelta(minutes=1),
                    override=True,
                )

        async with factory.begin() as session:
            with pytest.raises(InvalidStateTransitionError):
                await MonitoringService(session, settings).apply_fight_state(
                    fight_id=second_id,
                    target=FightStatus.COMPLETED,
                    source="provider",
                    idempotency_key=f"provider:{uuid4()}",
                    occurred_at=occurred_at + timedelta(minutes=20),
                )

        missing = await client.get(f"/api/v1/fights/{uuid4()}/prediction")
        assert missing.status_code == HTTPStatus.NOT_FOUND
    finally:
        async with factory() as session:
            await _cleanup(session, event_id, user_id)
        await engine.dispose()


async def _seed_card(session: AsyncSession) -> tuple[UUID, UUID, UUID, UUID]:
    suffix = uuid4().hex
    organization = Organization(name="Monitor Org", slug=suffix, active=True)
    athletes = [Athlete(name=f"Monitor {index}", external_ids={}) for index in range(4)]
    session.add_all([organization, *athletes])
    await session.flush()
    event = Event(
        organization_id=organization.id,
        name="Monitoring Event",
        slug=f"monitoring-{suffix}",
        scheduled_start_at=datetime.now(UTC),
        status=EventStatus.LIVE,
        provider_payload={},
        version=1,
    )
    session.add(event)
    await session.flush()
    first = Fight(
        event_id=event.id,
        red_athlete_id=athletes[0].id,
        blue_athlete_id=athletes[1].id,
        scheduled_order=1,
        current_order=1,
        rounds_scheduled=3,
        status=FightStatus.LIVE,
        provider_payload={},
        version=1,
    )
    second = Fight(
        event_id=event.id,
        red_athlete_id=athletes[2].id,
        blue_athlete_id=athletes[3].id,
        scheduled_order=2,
        current_order=2,
        rounds_scheduled=3,
        status=FightStatus.SCHEDULED,
        provider_payload={},
        version=1,
    )
    session.add_all([first, second])
    await session.flush()
    user = User(
        email=f"monitor-{suffix}@example.com",
        password_hash="unused",  # noqa: S106 - integration fixture only.
        display_name="Monitor User",
        locale="pt-BR",
        timezone="UTC",
        status="active",
        role="user",
    )
    session.add(user)
    await session.flush()
    device = Device(
        user_id=user.id,
        platform="android",
        push_token=f"monitor-token-{suffix}",
        app_version="1.0.0",
        notifications_enabled=True,
        last_seen_at=datetime.now(UTC),
    )
    alert = Alert(
        user_id=user.id,
        fight_id=second.id,
        trigger_type="next_fight",
        status="active",
    )
    session.add_all([device, alert])
    await session.commit()
    return event.id, first.id, second.id, user.id


async def _cleanup(session: AsyncSession, event_id: UUID, user_id: UUID) -> None:
    fights = list(
        await session.scalars(select(Fight).where(Fight.event_id == event_id))
    )
    fight_ids = [fight.id for fight in fights]
    athlete_ids = [
        athlete_id
        for fight in fights
        for athlete_id in (fight.red_athlete_id, fight.blue_athlete_id)
    ]
    alert_ids = select(Alert.id).where(Alert.user_id == user_id)
    await session.execute(
        delete(AlertDelivery).where(AlertDelivery.alert_id.in_(alert_ids))
    )
    await session.execute(delete(Alert).where(Alert.user_id == user_id))
    await session.execute(delete(Device).where(Device.user_id == user_id))
    await session.execute(delete(User).where(User.id == user_id))
    await session.execute(
        delete(OutboxEvent).where(
            OutboxEvent.payload["event_id"].astext == str(event_id)
        )
    )
    await session.execute(delete(Prediction).where(Prediction.fight_id.in_(fight_ids)))
    await session.execute(
        delete(FightStateEvent).where(FightStateEvent.event_id == event_id)
    )
    await session.execute(delete(Fight).where(Fight.event_id == event_id))
    event = await session.get(Event, event_id)
    await session.execute(delete(Event).where(Event.id == event_id))
    if event is not None:
        await session.execute(
            delete(Organization).where(Organization.id == event.organization_id)
        )
    await session.execute(delete(Athlete).where(Athlete.id.in_(athlete_ids)))
    await session.commit()
