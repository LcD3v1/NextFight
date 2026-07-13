"""Public timeline and prediction endpoints."""

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.modules.monitoring.api.schemas import PredictionResponse, TimelineItem
from nextfight.modules.monitoring.application.service import (
    MonitoringNotFoundError,
    MonitoringService,
)

router = APIRouter(tags=["Live Monitoring"])
NOT_FOUND = "Monitoring data not found."


@router.get("/events/{event_id}/timeline")
async def timeline(
    event_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> list[TimelineItem]:
    """Return an event's ordered live-state timeline."""
    try:
        items = await MonitoringService(session, request.app.state.settings).timeline(
            event_id
        )
    except MonitoringNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return [TimelineItem.model_validate(item) for item in items]


@router.get("/fights/{fight_id}/prediction")
async def prediction(
    fight_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> PredictionResponse:
    """Return the latest prediction for a fight."""
    try:
        item = await MonitoringService(
            session, request.app.state.settings
        ).latest_prediction(fight_id)
    except MonitoringNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return PredictionResponse.model_validate(item)
