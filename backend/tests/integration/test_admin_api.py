"""Administrative API integration tests with RBAC and audit evidence."""

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
    AuditLog,
    Device,
    Event,
    EventChange,
    Fight,
    FightStateEvent,
    Organization,
    OutboxEvent,
    Prediction,
    RefreshSession,
    User,
)
from nextfight.infrastructure.database.session import create_database_engine
from nextfight.modules.identity.domain.security import PasswordHasher


@pytest.mark.integration
async def test_admin_crud_live_control_rbac_and_audit(  # noqa: PLR0915
    client: httpx.AsyncClient,
    settings: Settings,
) -> None:
    """Create a card, reorder it, change state, and inspect immutable audit logs."""
    engine = create_database_engine(settings)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    email = f"admin-{uuid4()}@example.com"
    password = "Admin-integration-passphrase-42"  # noqa: S105 - test credential.
    async with factory() as session:
        admin_id = await _seed_admin(session, email, password)
    created: dict[str, list[UUID]] = {
        "organizations": [],
        "athletes": [],
        "events": [],
        "fights": [],
    }
    try:
        login = await client.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )
        assert login.status_code == HTTPStatus.OK
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        organization = await client.post(
            "/api/v1/admin/organizations",
            headers=headers,
            json={"name": "Admin Test Org", "slug": f"admin-org-{uuid4().hex}"},
        )
        assert organization.status_code == HTTPStatus.CREATED
        organization_id = UUID(organization.json()["id"])
        created["organizations"].append(organization_id)

        for name in ("Red One", "Blue One", "Red Two", "Blue Two"):
            response = await client.post(
                "/api/v1/admin/athletes",
                headers=headers,
                json={"name": name, "country_code": "BR"},
            )
            assert response.status_code == HTTPStatus.CREATED
            created["athletes"].append(UUID(response.json()["id"]))

        event = await client.post(
            "/api/v1/admin/events",
            headers=headers,
            json={
                "organization_id": str(organization_id),
                "name": "Admin Fight Night",
                "slug": f"admin-fight-night-{uuid4().hex}",
                "scheduled_start_at": (
                    datetime.now(UTC) + timedelta(days=1)
                ).isoformat(),
            },
        )
        assert event.status_code == HTTPStatus.CREATED
        event_id = UUID(event.json()["id"])
        created["events"].append(event_id)

        missing_event = await client.patch(
            f"/api/v1/admin/events/{uuid4()}",
            headers=headers,
            json={"name": "Missing Event"},
        )
        assert missing_event.status_code == HTTPStatus.NOT_FOUND
        missing_fight_create = await client.post(
            "/api/v1/admin/fights",
            headers=headers,
            json={
                "event_id": str(uuid4()),
                "red_athlete_id": str(created["athletes"][0]),
                "blue_athlete_id": str(created["athletes"][1]),
                "current_order": 99,
                "rounds_scheduled": 3,
            },
        )
        assert missing_fight_create.status_code == HTTPStatus.NOT_FOUND

        for index in range(2):
            fight = await client.post(
                "/api/v1/admin/fights",
                headers=headers,
                json={
                    "event_id": str(event_id),
                    "red_athlete_id": str(created["athletes"][index * 2]),
                    "blue_athlete_id": str(created["athletes"][index * 2 + 1]),
                    "current_order": index + 1,
                    "rounds_scheduled": 3,
                },
            )
            assert fight.status_code == HTTPStatus.CREATED
            created["fights"].append(UUID(fight.json()["id"]))

        invalid_card = await client.put(
            f"/api/v1/admin/events/{event_id}/card",
            headers=headers,
            json={"fight_ids": [str(created["fights"][0])]},
        )
        assert invalid_card.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        missing_fight_update = await client.patch(
            f"/api/v1/admin/fights/{uuid4()}",
            headers=headers,
            json={"weight_class": "Lightweight"},
        )
        assert missing_fight_update.status_code == HTTPStatus.NOT_FOUND

        reorder = await client.put(
            f"/api/v1/admin/events/{event_id}/card",
            headers=headers,
            json={"fight_ids": [str(item) for item in reversed(created["fights"])]},
        )
        assert reorder.status_code == HTTPStatus.NO_CONTENT

        event_state = await client.post(
            f"/api/v1/admin/events/{event_id}/state",
            headers=headers,
            json={
                "state": "live",
                "idempotency_key": f"admin-event-{uuid4()}",
            },
        )
        assert event_state.status_code == HTTPStatus.OK

        fight_state = await client.post(
            f"/api/v1/admin/fights/{created['fights'][0]}/state",
            headers=headers,
            json={
                "state": "next",
                "idempotency_key": f"admin-fight-{uuid4()}",
                "occurred_at": datetime.now(UTC).isoformat(),
            },
        )
        assert fight_state.status_code == HTTPStatus.CREATED

        alert = await client.post(
            "/api/v1/me/alerts",
            headers=headers,
            json={
                "fight_id": str(created["fights"][0]),
                "trigger_type": "next_fight",
            },
        )
        assert alert.status_code == HTTPStatus.CREATED
        device = await client.post(
            "/api/v1/me/devices",
            headers=headers,
            json={
                "platform": "android",
                "push_token": f"admin-provider-token-{uuid4().hex}",
                "app_version": "1.0.0",
            },
        )
        assert device.status_code == HTTPStatus.CREATED
        dispatch_payload = {
            "alert_id": alert.json()["id"],
            "idempotency_key": f"manual-{uuid4()}",
            "title": "Manual operations update",
            "body": "The fight status requires your attention.",
        }
        dispatch = await client.post(
            "/api/v1/admin/alerts/dispatch",
            headers=headers,
            json=dispatch_payload,
        )
        assert dispatch.status_code == HTTPStatus.ACCEPTED
        assert dispatch.json()["queued"] == 1
        duplicate_dispatch = await client.post(
            "/api/v1/admin/alerts/dispatch",
            headers=headers,
            json=dispatch_payload,
        )
        assert duplicate_dispatch.json()["queued"] == 0

        dashboard = await client.get("/api/v1/admin/dashboard", headers=headers)
        assert dashboard.status_code == HTTPStatus.OK
        assert dashboard.json()["live_events"] >= 1
        for endpoint in ("organizations", "athletes", "users", "deliveries"):
            catalog = await client.get(f"/api/v1/admin/{endpoint}", headers=headers)
            assert catalog.status_code == HTTPStatus.OK
        logs = await client.get(
            "/api/v1/admin/audit-logs", headers=headers, params={"limit": 50}
        )
        assert logs.status_code == HTTPStatus.OK
        actions = {item["action"] for item in logs.json()}
        assert {"event.created", "card.reordered", "fight.state_changed"} <= actions

        regular = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"regular-{uuid4()}@example.com",
                "password": "Regular-integration-passphrase-42",
                "display_name": "Regular User",
            },
        )
        regular_id = UUID(regular.json()["user"]["id"])
        denied = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {regular.json()['access_token']}"},
        )
        assert denied.status_code == HTTPStatus.FORBIDDEN
        async with factory() as session:
            await _delete_user(session, regular_id)
    finally:
        async with factory() as session:
            await _cleanup(session, admin_id, created)
        await engine.dispose()


async def _seed_admin(session: AsyncSession, email: str, password: str) -> UUID:
    admin = User(
        email=email,
        password_hash=PasswordHasher().hash(password),
        display_name="Admin Test",
        locale="en",
        timezone="UTC",
        status="active",
        role="admin",
    )
    session.add(admin)
    await session.commit()
    return admin.id


async def _delete_user(session: AsyncSession, user_id: UUID) -> None:
    await session.execute(
        delete(RefreshSession).where(RefreshSession.user_id == user_id)
    )
    await session.execute(delete(User).where(User.id == user_id))
    await session.commit()


async def _cleanup(
    session: AsyncSession,
    admin_id: UUID,
    created: dict[str, list[UUID]],
) -> None:
    fight_ids = created["fights"]
    event_ids = created["events"]
    user_alert_ids = select(Alert.id).where(Alert.user_id == admin_id)
    await session.execute(
        delete(AlertDelivery).where(AlertDelivery.alert_id.in_(user_alert_ids))
    )
    await session.execute(delete(Alert).where(Alert.user_id == admin_id))
    await session.execute(delete(Device).where(Device.user_id == admin_id))
    await session.execute(delete(Prediction).where(Prediction.fight_id.in_(fight_ids)))
    await session.execute(
        delete(FightStateEvent).where(FightStateEvent.fight_id.in_(fight_ids))
    )
    await session.execute(
        delete(OutboxEvent).where(
            OutboxEvent.payload["event_id"].astext.in_(
                [str(item) for item in event_ids]
            )
        )
    )
    await session.execute(
        delete(EventChange).where(EventChange.event_id.in_(event_ids))
    )
    await session.execute(delete(Fight).where(Fight.id.in_(fight_ids)))
    await session.execute(delete(Event).where(Event.id.in_(event_ids)))
    await session.execute(delete(Athlete).where(Athlete.id.in_(created["athletes"])))
    await session.execute(
        delete(Organization).where(Organization.id.in_(created["organizations"]))
    )
    await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == admin_id))
    await _delete_user(session, admin_id)
