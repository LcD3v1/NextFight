"""Authenticated engagement API integration tests."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Alert,
    Athlete,
    Device,
    Event,
    EventStatus,
    Favorite,
    Fight,
    FightStatus,
    Organization,
    User,
)
from nextfight.infrastructure.database.session import create_database_engine


@pytest.mark.integration
async def test_favorites_alerts_and_devices_lifecycle(  # noqa: PLR0915
    client: httpx.AsyncClient,
    settings: Settings,
) -> None:
    """Exercise all user-owned engagement resources with real persistence."""
    engine = create_database_engine(settings)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        event_id, fight_id = await _seed_fight(session)
    user_id: UUID | None = None
    try:
        registration = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"engagement-{uuid4()}@example.com",
                "password": "Engagement-integration-passphrase-42",
                "display_name": "Engagement Test",
            },
        )
        assert registration.status_code == HTTPStatus.CREATED
        user_id = UUID(registration.json()["user"]["id"])
        headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

        favorite = await client.post(
            "/api/v1/me/favorites",
            headers=headers,
            json={"target_type": "event", "target_id": str(event_id)},
        )
        assert favorite.status_code == HTTPStatus.CREATED
        favorite_id = favorite.json()["id"]
        duplicate = await client.post(
            "/api/v1/me/favorites",
            headers=headers,
            json={"target_type": "event", "target_id": str(event_id)},
        )
        assert duplicate.json()["id"] == favorite_id
        assert (
            len((await client.get("/api/v1/me/favorites", headers=headers)).json()) == 1
        )

        invalid_favorite = await client.post(
            "/api/v1/me/favorites",
            headers=headers,
            json={"target_type": "athlete", "target_id": str(uuid4())},
        )
        assert invalid_favorite.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        missing_favorite = await client.delete(
            f"/api/v1/me/favorites/{uuid4()}", headers=headers
        )
        assert missing_favorite.status_code == HTTPStatus.NOT_FOUND

        alert = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={
                "fight_id": str(fight_id),
                "trigger_type": "lead_time",
                "lead_minutes": 15,
            },
        )
        assert alert.status_code == HTTPStatus.CREATED
        alert_id = alert.json()["id"]
        duplicate_alert = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={
                "fight_id": str(fight_id),
                "trigger_type": "lead_time",
                "lead_minutes": 15,
            },
        )
        assert duplicate_alert.json()["id"] == alert_id
        missing_lead = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={"fight_id": str(fight_id), "trigger_type": "lead_time"},
        )
        assert missing_lead.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        missing_fight = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={"fight_id": str(uuid4()), "trigger_type": "walkouts"},
        )
        assert missing_fight.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        next_alert = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={"fight_id": str(fight_id), "trigger_type": "next_fight"},
        )
        assert next_alert.status_code == HTTPStatus.CREATED
        invalid_change = await client.patch(
            f"/api/v1/me/alerts/{next_alert.json()['id']}",
            headers=headers,
            json={"lead_minutes": 5},
        )
        assert invalid_change.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        changed = await client.patch(
            f"/api/v1/me/alerts/{alert_id}",
            headers=headers,
            json={"status": "paused", "lead_minutes": 10},
        )
        assert changed.status_code == HTTPStatus.OK
        assert changed.json()["status"] == "paused"
        assert (
            len((await client.get("/api/v1/me/alerts", headers=headers)).json()) == 2  # noqa: PLR2004 - two intentionally distinct trigger configurations.
        )
        missing_alert = await client.patch(
            f"/api/v1/me/alerts/{uuid4()}",
            headers=headers,
            json={"status": "paused"},
        )
        assert missing_alert.status_code == HTTPStatus.NOT_FOUND

        provider_token = f"provider-token-{uuid4().hex}"
        device = await client.post(
            "/api/v1/me/devices",
            headers=headers,
            json={
                "platform": "android",
                "push_token": provider_token,
                "app_version": "1.0.0",
            },
        )
        assert device.status_code == HTTPStatus.CREATED
        device_id = device.json()["id"]
        assert "push_token" not in device.json()
        refreshed_device = await client.post(
            "/api/v1/me/devices",
            headers=headers,
            json={
                "platform": "android",
                "push_token": provider_token,
                "app_version": "1.0.1",
                "notifications_enabled": False,
            },
        )
        assert refreshed_device.json()["id"] == device_id
        assert refreshed_device.json()["notifications_enabled"] is False
        assert (
            len((await client.get("/api/v1/me/devices", headers=headers)).json()) == 1
        )

        assert (
            await client.delete(f"/api/v1/me/devices/{device_id}", headers=headers)
        ).status_code == HTTPStatus.NO_CONTENT
        missing_device = await client.delete(
            f"/api/v1/me/devices/{uuid4()}", headers=headers
        )
        assert missing_device.status_code == HTTPStatus.NOT_FOUND
        assert (
            await client.delete(f"/api/v1/me/alerts/{alert_id}", headers=headers)
        ).status_code == HTTPStatus.NO_CONTENT
        assert (
            await client.delete(f"/api/v1/me/favorites/{favorite_id}", headers=headers)
        ).status_code == HTTPStatus.NO_CONTENT
    finally:
        async with factory() as session:
            await _cleanup(session, event_id, user_id)
        await engine.dispose()


async def _seed_fight(session: AsyncSession) -> tuple[UUID, UUID]:
    suffix = uuid4().hex
    organization = Organization(name="Engagement Org", slug=suffix, active=True)
    red = Athlete(name="Engagement Red", external_ids={})
    blue = Athlete(name="Engagement Blue", external_ids={})
    session.add_all([organization, red, blue])
    await session.flush()
    event = Event(
        organization_id=organization.id,
        name="Engagement Event",
        slug=f"engagement-{suffix}",
        scheduled_start_at=datetime.now(UTC) + timedelta(days=1),
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
    session.add(fight)
    await session.commit()
    return event.id, fight.id


async def _cleanup(session: AsyncSession, event_id: UUID, user_id: UUID | None) -> None:
    fight_ids = (
        Fight.__table__.select()
        .with_only_columns(Fight.id)
        .where(Fight.event_id == event_id)
    )
    if user_id is not None:
        await session.execute(delete(Alert).where(Alert.user_id == user_id))
        await session.execute(delete(Favorite).where(Favorite.user_id == user_id))
        await session.execute(delete(Device).where(Device.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
    event = await session.get(Event, event_id)
    athlete_rows = (
        await session.execute(
            Fight.__table__.select()
            .with_only_columns(Fight.red_athlete_id, Fight.blue_athlete_id)
            .where(Fight.event_id == event_id)
        )
    ).all()
    await session.execute(delete(Fight).where(Fight.id.in_(fight_ids)))
    await session.execute(delete(Event).where(Event.id == event_id))
    if event is not None:
        await session.execute(
            delete(Organization).where(Organization.id == event.organization_id)
        )
    athlete_ids = [item for row in athlete_rows for item in row]
    await session.execute(delete(Athlete).where(Athlete.id.in_(athlete_ids)))
    await session.commit()
