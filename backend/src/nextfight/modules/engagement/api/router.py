"""Authenticated favorites, alerts, and devices endpoints."""

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.infrastructure.database.entities import User
from nextfight.modules.engagement.api.schemas import (
    AlertCreate,
    AlertResponse,
    AlertUpdate,
    DeviceCreate,
    DeviceResponse,
    FavoriteCreate,
    FavoriteResponse,
)
from nextfight.modules.engagement.application.service import (
    EngagementNotFoundError,
    EngagementService,
    InvalidEngagementTargetError,
)
from nextfight.modules.identity.api.dependencies import get_current_user

router = APIRouter(prefix="/me", tags=["Engagement"])
NOT_FOUND = "Resource not found."
INVALID_TARGET = "The referenced resource or alert configuration is invalid."


def _service(session: AsyncSession, user: User) -> EngagementService:
    return EngagementService(session, user.id)


@router.get("/favorites")
async def list_favorites(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[FavoriteResponse]:
    """List current user's favorites."""
    return [
        FavoriteResponse.model_validate(item)
        for item in await _service(session, user).list_favorites()
    ]


@router.post("/favorites", status_code=HTTPStatus.CREATED)
async def create_favorite(
    payload: FavoriteCreate,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> FavoriteResponse:
    """Create an idempotent favorite."""
    try:
        item = await _service(session, user).create_favorite(payload)
    except InvalidEngagementTargetError as error:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, INVALID_TARGET) from error
    return FavoriteResponse.model_validate(item)


@router.delete("/favorites/{favorite_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_favorite(
    favorite_id: UUID,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Delete an owned favorite."""
    try:
        await _service(session, user).delete_favorite(favorite_id)
    except EngagementNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/alerts")
async def list_alerts(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[AlertResponse]:
    """List current user's alert history."""
    return [
        AlertResponse.model_validate(item)
        for item in await _service(session, user).list_alerts()
    ]


@router.post("/alerts", status_code=HTTPStatus.CREATED)
async def create_alert(
    payload: AlertCreate,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> AlertResponse:
    """Create or reactivate a fight alert."""
    try:
        item = await _service(session, user).create_alert(payload)
    except InvalidEngagementTargetError as error:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, INVALID_TARGET) from error
    return AlertResponse.model_validate(item)


@router.patch("/alerts/{alert_id}")
async def update_alert(
    alert_id: UUID,
    payload: AlertUpdate,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> AlertResponse:
    """Change an owned alert preference."""
    try:
        item = await _service(session, user).update_alert(alert_id, payload)
    except EngagementNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    except InvalidEngagementTargetError as error:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, INVALID_TARGET) from error
    return AlertResponse.model_validate(item)


@router.delete("/alerts/{alert_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Cancel an alert while preserving its history."""
    try:
        await _service(session, user).delete_alert(alert_id)
    except EngagementNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/devices")
async def list_devices(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[DeviceResponse]:
    """List current user's push devices."""
    return [
        DeviceResponse.model_validate(item)
        for item in await _service(session, user).list_devices()
    ]


@router.post("/devices", status_code=HTTPStatus.CREATED)
async def register_device(
    payload: DeviceCreate,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> DeviceResponse:
    """Register or refresh a push provider token."""
    return DeviceResponse.model_validate(
        await _service(session, user).register_device(payload)
    )


@router.delete("/devices/{device_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_device(
    device_id: UUID,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Delete an owned push device."""
    try:
        await _service(session, user).delete_device(device_id)
    except EngagementNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return Response(status_code=HTTPStatus.NO_CONTENT)
