"""Authentication and role-based authorization dependencies."""

from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.infrastructure.database.entities import User
from nextfight.modules.identity.domain.security import (
    InvalidAccessTokenError,
    TokenService,
)

bearer_scheme = HTTPBearer(auto_error=False)
AUTHENTICATION_REQUIRED = "Authentication is required."
ACCESS_DENIED = "You do not have permission to perform this action."


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> User:
    """Resolve an active user from a validated bearer access token."""
    if credentials is None or credentials.scheme.casefold() != "bearer":
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=AUTHENTICATION_REQUIRED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = TokenService(request.app.state.settings).decode_access_token(
            credentials.credentials
        )
    except InvalidAccessTokenError as error:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=AUTHENTICATION_REQUIRED,
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    user = await session.get(User, claims.subject)
    if user is None or user.status != "active" or user.role != claims.role:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=AUTHENTICATION_REQUIRED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(*allowed_roles: str) -> Callable[..., Awaitable[User]]:
    """Create a dependency that permits only explicitly listed roles."""

    async def authorize(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=ACCESS_DENIED,
            )
        return user

    return authorize
