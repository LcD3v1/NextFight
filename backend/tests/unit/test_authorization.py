"""Role authorization dependency tests."""

from http import HTTPStatus

import pytest
from fastapi import HTTPException

from nextfight.infrastructure.database.entities import User
from nextfight.modules.identity.api.dependencies import require_roles


def _user(role: str) -> User:
    return User(
        email=f"{role}@example.com",
        password_hash="unused",  # noqa: S106 - authorization-only unit fixture.
        display_name=role.title(),
        locale="en",
        timezone="UTC",
        status="active",
        role=role,
    )


@pytest.mark.asyncio
async def test_role_dependency_allows_listed_role() -> None:
    """Return the principal when its role is explicitly allowed."""
    admin = _user("admin")
    authorize = require_roles("admin", "operator")
    assert await authorize(admin) is admin


@pytest.mark.asyncio
async def test_role_dependency_rejects_unlisted_role() -> None:
    """Reject a valid principal that lacks the required role."""
    authorize = require_roles("admin")
    with pytest.raises(HTTPException) as captured:
        await authorize(_user("user"))
    assert captured.value.status_code == HTTPStatus.FORBIDDEN
