"""Prediction-based lead-time scheduling integration tests."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Alert,
    AlertDelivery,
    Athlete,
    Device,
    Event,
    EventStatus,
    Fight,
    FightStatus,
    Organization,
    Prediction,
    User,
)
from nextfight.infrastructure.database.session import create_database_engine
from nextfight.infrastructure.notifications.scheduler import LeadTimeAlertScheduler


@pytest.mark.integration
async def test_scheduler_creates_one_idempotent_localized_delivery(
    settings: Settings,
) -> None:
    """Schedule a due prediction once even when multiple workers poll it."""
    engine = create_database_engine(settings)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    suffix = uuid4().hex
    async with sessions.begin() as session:
        organization = Organization(name="Scheduler Org", slug=suffix, active=True)
        red = Athlete(name="Scheduler Red", external_ids={})
        blue = Athlete(name="Scheduler Blue", external_ids={})
        user = User(
            email=f"scheduler-{suffix}@example.com",
            password_hash="not-used-in-this-test",  # noqa: S106
            display_name="Scheduler User",
            locale="pt",
            timezone="UTC",
            status="active",
            role="user",
        )
        session.add_all([organization, red, blue, user])
        await session.flush()
        event = Event(
            organization_id=organization.id,
            name="Scheduler Event",
            slug=f"scheduler-{suffix}",
            scheduled_start_at=datetime.now(UTC) + timedelta(hours=1),
            status=EventStatus.SCHEDULED,
            provider_payload={},
            version=1,
        )
        session.add(event)
        await session.flush()
        fight = Fight(
            event_id=event.id,
            red_athlete_id=red.id,
            blue_athlete_id=blue.id,
            scheduled_order=1,
            current_order=1,
            rounds_scheduled=3,
            status=FightStatus.SCHEDULED,
            provider_payload={},
            version=1,
        )
        device = Device(
            user_id=user.id,
            platform="android",
            push_token=f"scheduler-token-{suffix}",
            app_version="1.0.0",
            notifications_enabled=True,
            last_seen_at=datetime.now(UTC),
        )
        session.add_all([fight, device])
        await session.flush()
        alert = Alert(
            user_id=user.id,
            fight_id=fight.id,
            trigger_type="lead_time",
            lead_minutes=15,
            status="active",
        )
        prediction = Prediction(
            fight_id=fight.id,
            predicted_start_at=datetime.now(UTC) + timedelta(minutes=10),
            earliest_start_at=datetime.now(UTC) + timedelta(minutes=8),
            latest_start_at=datetime.now(UTC) + timedelta(minutes=12),
            confidence_score=0.8,
            model_version="test-v1",
            factors={},
        )
        session.add_all([alert, prediction])

    scheduler = LeadTimeAlertScheduler(engine)
    try:
        assert await scheduler.schedule_due() == 1
        assert await scheduler.schedule_due() == 0
        async with sessions() as session:
            delivery = await session.scalar(
                select(AlertDelivery).where(AlertDelivery.alert_id == alert.id)
            )
            assert delivery is not None
            assert delivery.status == "pending"
            assert delivery.data["type"] == "fight.lead_time"
            assert delivery.title == "Sua luta está se aproximando"
    finally:
        async with sessions.begin() as session:
            await session.execute(
                delete(AlertDelivery).where(AlertDelivery.alert_id == alert.id)
            )
            await session.execute(
                delete(Prediction).where(Prediction.fight_id == fight.id)
            )
            await session.execute(delete(Alert).where(Alert.id == alert.id))
            await session.execute(delete(Device).where(Device.id == device.id))
            await session.execute(delete(Fight).where(Fight.id == fight.id))
            await session.execute(delete(Event).where(Event.id == event.id))
            await session.execute(delete(User).where(User.id == user.id))
            await session.execute(
                delete(Organization).where(Organization.id == organization.id)
            )
            await session.execute(
                delete(Athlete).where(Athlete.id.in_((red.id, blue.id)))
            )
        await engine.dispose()
