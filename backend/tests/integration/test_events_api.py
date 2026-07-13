"""Public event API integration tests against PostgreSQL."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import (
    Athlete,
    Event,
    EventStatus,
    Fight,
    FightStatus,
    Organization,
)
from nextfight.infrastructure.database.session import create_database_engine


@pytest.mark.integration
async def test_event_list_detail_and_ordered_card(
    client: httpx.AsyncClient,
    settings: Settings,
) -> None:
    """Expose seeded domain data through stable public projections."""
    engine = create_database_engine(settings)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        event_id = await _seed_event(session)
    try:
        listing = await client.get(
            "/api/v1/events", params={"statuses": "scheduled", "limit": 100}
        )
        assert listing.status_code == HTTPStatus.OK
        listed = next(
            item for item in listing.json()["items"] if item["id"] == str(event_id)
        )
        assert listed["organization"]["slug"].startswith("test-org-")

        detail = await client.get(f"/api/v1/events/{event_id}")
        assert detail.status_code == HTTPStatus.OK
        fights = detail.json()["fights"]
        assert [fight["current_order"] for fight in fights] == [1, 2]
        assert fights[0]["red_athlete"]["name"] == "Red Two"

        card = await client.get(f"/api/v1/events/{event_id}/fights")
        assert card.status_code == HTTPStatus.OK
        assert card.json() == fights

        fight = await client.get(f"/api/v1/fights/{fights[0]['id']}")
        assert fight.status_code == HTTPStatus.OK
        assert fight.json() == fights[0]

        missing_fight = await client.get(f"/api/v1/fights/{uuid4()}")
        assert missing_fight.status_code == HTTPStatus.NOT_FOUND

        missing = await client.get(f"/api/v1/events/{uuid4()}")
        assert missing.status_code == HTTPStatus.NOT_FOUND
    finally:
        async with factory() as session:
            await _delete_event_fixture(session, event_id)
        await engine.dispose()


async def _seed_event(session: AsyncSession) -> UUID:
    suffix = uuid4().hex
    organization = Organization(
        name="Test Organization", slug=f"test-org-{suffix}", active=True
    )
    athletes = [
        Athlete(name="Red One", external_ids={}),
        Athlete(name="Blue One", external_ids={}),
        Athlete(name="Red Two", external_ids={}),
        Athlete(name="Blue Two", external_ids={}),
    ]
    session.add_all([organization, *athletes])
    await session.flush()
    event = Event(
        organization_id=organization.id,
        name="Integration Fight Night",
        slug=f"integration-fight-night-{suffix}",
        scheduled_start_at=datetime.now(UTC) + timedelta(days=1),
        status=EventStatus.SCHEDULED,
        provider_payload={},
        version=1,
    )
    session.add(event)
    await session.flush()
    session.add_all(
        [
            Fight(
                event_id=event.id,
                red_athlete_id=athletes[0].id,
                blue_athlete_id=athletes[1].id,
                scheduled_order=1,
                current_order=2,
                rounds_scheduled=3,
                status=FightStatus.SCHEDULED,
                provider_payload={},
                version=1,
            ),
            Fight(
                event_id=event.id,
                red_athlete_id=athletes[2].id,
                blue_athlete_id=athletes[3].id,
                scheduled_order=2,
                current_order=1,
                rounds_scheduled=3,
                status=FightStatus.NEXT,
                provider_payload={},
                version=1,
            ),
        ]
    )
    await session.commit()
    return event.id


async def _delete_event_fixture(session: AsyncSession, event_id: UUID) -> None:
    event = await session.get(Event, event_id)
    if event is None:
        return
    athlete_ids = (
        await session.execute(
            Fight.__table__.select()
            .with_only_columns(Fight.red_athlete_id, Fight.blue_athlete_id)
            .where(Fight.event_id == event_id)
        )
    ).all()
    await session.execute(delete(Fight).where(Fight.event_id == event_id))
    await session.execute(delete(Event).where(Event.id == event_id))
    await session.execute(
        delete(Organization).where(Organization.id == event.organization_id)
    )
    flat_ids = [athlete_id for pair in athlete_ids for athlete_id in pair]
    await session.execute(delete(Athlete).where(Athlete.id.in_(flat_ids)))
    await session.commit()
