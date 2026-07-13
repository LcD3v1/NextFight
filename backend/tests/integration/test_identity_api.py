"""Identity API integration tests against PostgreSQL."""

from http import HTTPStatus
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from nextfight.core.config import Settings
from nextfight.infrastructure.database.entities import User
from nextfight.infrastructure.database.session import create_database_engine


@pytest.mark.integration
async def test_authentication_session_lifecycle(
    client: httpx.AsyncClient,
    settings: Settings,
) -> None:
    """Register, login, rotate, detect reuse, and revoke a real session."""
    email = f"identity-{uuid4()}@example.com"
    password = "A-production-grade-passphrase-42"  # noqa: S105 - test credential.
    user_id: UUID | None = None
    try:
        registration = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email.replace("identity", "IDENTITY"),
                "password": password,
                "display_name": "Identity Test",
            },
        )
        assert registration.status_code == HTTPStatus.CREATED
        registered = registration.json()
        user_id = UUID(registered["user"]["id"])
        assert registered["user"]["email"] == email
        assert registered["token_type"] == "bearer"  # noqa: S105 - OAuth scheme.
        assert registered["expires_in"] == settings.access_token_minutes * 60
        assert len(registered["refresh_token"]) >= 64  # noqa: PLR2004

        duplicate = await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "display_name": "Duplicate",
            },
        )
        assert duplicate.status_code == HTTPStatus.CONFLICT
        assert duplicate.headers["content-type"].startswith("application/problem+json")

        invalid = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "incorrect"},
        )
        assert invalid.status_code == HTTPStatus.UNAUTHORIZED

        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login.status_code == HTTPStatus.OK
        original_refresh = login.json()["refresh_token"]

        rotation = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": original_refresh},
        )
        assert rotation.status_code == HTTPStatus.OK
        replacement_refresh = rotation.json()["refresh_token"]
        assert replacement_refresh != original_refresh

        reuse = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": original_refresh},
        )
        assert reuse.status_code == HTTPStatus.UNAUTHORIZED

        compromised_replacement = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": replacement_refresh},
        )
        assert compromised_replacement.status_code == HTTPStatus.UNAUTHORIZED

        logout = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": registered["refresh_token"]},
        )
        assert logout.status_code == HTTPStatus.NO_CONTENT
    finally:
        if user_id is not None:
            engine = create_database_engine(settings)
            session_factory = async_sessionmaker(engine, expire_on_commit=False)
            async with session_factory() as session:
                await _delete_test_user(session, user_id)
            await engine.dispose()


async def _delete_test_user(session: AsyncSession, user_id: UUID) -> None:
    """Remove test-owned records using database cascades."""
    await session.execute(delete(User).where(User.id == user_id))
    await session.commit()


@pytest.mark.integration
async def test_identity_payload_validation(client: httpx.AsyncClient) -> None:
    """Reject weak and structurally invalid registration payloads."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid", "password": "short", "display_name": "x"},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.json()
    assert body["type"].endswith("validation-error")
    assert len(body["errors"]) == 3  # noqa: PLR2004
