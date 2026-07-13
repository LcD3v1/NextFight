"""Public event and fight-card endpoints."""

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.infrastructure.database.entities import EventStatus
from nextfight.modules.events.api.schemas import (
    EventDetail,
    EventListResponse,
    FightResponse,
)
from nextfight.modules.events.application.service import (
    EventNotFoundError,
    EventQueryService,
)

router = APIRouter(tags=["Events"])
EVENT_NOT_FOUND = "Event not found."


@router.get("/events")
async def list_events(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    statuses: Annotated[list[EventStatus] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> EventListResponse:
    """List upcoming and live events by default."""
    selected = tuple(statuses or (EventStatus.SCHEDULED, EventStatus.LIVE))
    return await EventQueryService(session).list_events(statuses=selected, limit=limit)


@router.get("/events/{event_id}")
async def get_event(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> EventDetail:
    """Return an event with its current ordered card."""
    try:
        return await EventQueryService(session).get_event(event_id)
    except EventNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, EVENT_NOT_FOUND) from error


@router.get("/events/{event_id}/fights")
async def list_fights(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> list[FightResponse]:
    """Return the current fight-card order for an event."""
    service = EventQueryService(session)
    try:
        await service.get_event(event_id)
    except EventNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, EVENT_NOT_FOUND) from error
    return await service.list_fights(event_id)
