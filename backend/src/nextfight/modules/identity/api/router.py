"""Identity authentication endpoints."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.core.config import Settings
from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.infrastructure.database.entities import User
from nextfight.modules.identity.api.dependencies import get_current_user
from nextfight.modules.identity.api.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from nextfight.modules.identity.application.service import (
    IdentityError,
    IdentityService,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    """Return the current authenticated user's public profile."""
    return UserResponse.model_validate(user, from_attributes=True)


def _client_context(request: Request) -> tuple[str | None, str | None]:
    return request.headers.get(
        "user-agent"
    ), request.client.host if request.client else None


def _response(
    user: object, access: str, refresh: str, settings: Settings
) -> TokenResponse:
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.access_token_minutes * 60,
        user=UserResponse.model_validate(user, from_attributes=True),
    )


def _translate(error: IdentityError) -> HTTPException:
    status = (
        HTTPStatus.CONFLICT
        if error.code == "email_unavailable"
        else HTTPStatus.UNAUTHORIZED
    )
    return HTTPException(status_code=status, detail=str(error))


@router.post("/register", status_code=HTTPStatus.CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> TokenResponse:
    """Register an account and return its first token pair."""
    service = IdentityService(session, request.app.state.settings)
    try:
        user, access, refresh = await service.register(
            payload.email,
            payload.password,
            payload.display_name,
            user_agent=_client_context(request)[0],
            ip_address=_client_context(request)[1],
        )
    except IdentityError as error:
        raise _translate(error) from error
    return _response(user, access, refresh, request.app.state.settings)


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> TokenResponse:
    """Authenticate an active account with email and password."""
    try:
        user, access, refresh = await IdentityService(
            session, request.app.state.settings
        ).login(
            payload.email,
            payload.password,
            user_agent=_client_context(request)[0],
            ip_address=_client_context(request)[1],
        )
    except IdentityError as error:
        raise _translate(error) from error
    return _response(user, access, refresh, request.app.state.settings)


@router.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> TokenResponse:
    """Rotate a refresh token and return a replacement pair."""
    try:
        user, access, replacement = await IdentityService(
            session, request.app.state.settings
        ).refresh(
            payload.refresh_token,
            user_agent=_client_context(request)[0],
            ip_address=_client_context(request)[1],
        )
    except IdentityError as error:
        raise _translate(error) from error
    return _response(user, access, replacement, request.app.state.settings)


@router.post("/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> Response:
    """Revoke a refresh token idempotently."""
    await IdentityService(session, request.app.state.settings).logout(
        payload.refresh_token
    )
    return Response(status_code=HTTPStatus.NO_CONTENT)
