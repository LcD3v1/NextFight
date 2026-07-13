"""Role-protected and audited administrative endpoints."""

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.dependencies import get_database_session
from nextfight.infrastructure.database.entities import User
from nextfight.modules.admin.api.schemas import (
    AthleteAdminResponse,
    AthleteCreate,
    AuditLogResponse,
    CardOrderCommand,
    DashboardResponse,
    DeliveryAdminResponse,
    EntityResponse,
    EventCreate,
    EventStateCommand,
    EventUpdate,
    FightCreate,
    FightStateCommand,
    FightUpdate,
    OrganizationAdminResponse,
    OrganizationCreate,
    UserAdminResponse,
)
from nextfight.modules.admin.application.service import (
    AdminNotFoundError,
    AdminService,
    InvalidCardOrderError,
)
from nextfight.modules.identity.api.dependencies import require_roles
from nextfight.modules.monitoring.application.service import MonitoringNotFoundError
from nextfight.modules.monitoring.domain.state_machine import (
    InvalidStateTransitionError,
)

router = APIRouter(prefix="/admin", tags=["Administration"])
AdminPrincipal = Annotated[User, Depends(require_roles("admin", "operator"))]
NOT_FOUND = "Administrative target not found."
INVALID_OPERATION = "The requested administrative operation is invalid."
ADMIN_OVERRIDE_REQUIRED = "Only administrators may override state policy."


def _service(session: AsyncSession, request: Request, actor: User) -> AdminService:
    return AdminService(
        session,
        request.app.state.settings,
        actor,
        request.client.host if request.client else None,
    )


@router.get("/dashboard")
async def dashboard(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> DashboardResponse:
    """Return live operational counters."""
    return await _service(session, request, actor).dashboard()


@router.post("/organizations", status_code=HTTPStatus.CREATED)
async def create_organization(
    payload: OrganizationCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Create an organization."""
    entity = await _service(session, request, actor).create_organization(payload)
    return EntityResponse(id=entity.id)


@router.post("/athletes", status_code=HTTPStatus.CREATED)
async def create_athlete(
    payload: AthleteCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Create an athlete."""
    entity = await _service(session, request, actor).create_athlete(payload)
    return EntityResponse(id=entity.id)


@router.post("/events", status_code=HTTPStatus.CREATED)
async def create_event(
    payload: EventCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Create a scheduled event."""
    try:
        entity = await _service(session, request, actor).create_event(payload)
    except AdminNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return EntityResponse(id=entity.id, version=entity.version)


@router.patch("/events/{event_id}")
async def update_event(
    event_id: UUID,
    payload: EventUpdate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Update event metadata."""
    try:
        entity = await _service(session, request, actor).update_event(event_id, payload)
    except AdminNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return EntityResponse(id=entity.id, version=entity.version)


@router.post("/fights", status_code=HTTPStatus.CREATED)
async def create_fight(
    payload: FightCreate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Add a fight to an event card."""
    try:
        entity = await _service(session, request, actor).create_fight(payload)
    except AdminNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return EntityResponse(id=entity.id, version=entity.version)


@router.patch("/fights/{fight_id}")
async def update_fight(
    fight_id: UUID,
    payload: FightUpdate,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Update fight metadata."""
    try:
        entity = await _service(session, request, actor).update_fight(fight_id, payload)
    except AdminNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    return EntityResponse(id=entity.id, version=entity.version)


@router.post("/events/{event_id}/state")
async def change_event_state(
    event_id: UUID,
    payload: EventStateCommand,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Apply a manual event state transition."""
    _ensure_override_role(actor, override=payload.override)
    try:
        entity = await _service(session, request, actor).apply_event_state(
            event_id, payload
        )
    except AdminNotFoundError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    except InvalidStateTransitionError as error:
        raise HTTPException(HTTPStatus.CONFLICT, str(error)) from error
    return EntityResponse(id=entity.id, version=entity.version)


@router.post("/fights/{fight_id}/state", status_code=HTTPStatus.CREATED)
async def change_fight_state(
    fight_id: UUID,
    payload: FightStateCommand,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> EntityResponse:
    """Apply a manual fight-state observation."""
    _ensure_override_role(actor, override=payload.override)
    try:
        observation_id = await _service(session, request, actor).apply_fight_state(
            fight_id, payload
        )
    except (AdminNotFoundError, MonitoringNotFoundError) as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, NOT_FOUND) from error
    except InvalidStateTransitionError as error:
        raise HTTPException(HTTPStatus.CONFLICT, str(error)) from error
    return EntityResponse(id=observation_id)


@router.put("/events/{event_id}/card", status_code=HTTPStatus.NO_CONTENT)
async def reorder_card(
    event_id: UUID,
    payload: CardOrderCommand,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
) -> Response:
    """Atomically replace the current event card order."""
    try:
        await _service(session, request, actor).reorder_card(
            event_id, payload.fight_ids
        )
    except InvalidCardOrderError as error:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY, INVALID_OPERATION
        ) from error
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/audit-logs")
async def audit_logs(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[AuditLogResponse]:
    """Return recent privileged-operation audit logs."""
    logs = await _service(session, request, actor).audit_logs(limit)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/organizations")
async def organizations(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> list[OrganizationAdminResponse]:
    """Return the organization catalog."""
    items = await _service(session, request, actor).organizations(limit)
    return [OrganizationAdminResponse.model_validate(item) for item in items]


@router.get("/athletes")
async def athletes(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> list[AthleteAdminResponse]:
    """Return the athlete catalog."""
    items = await _service(session, request, actor).athletes(limit)
    return [AthleteAdminResponse.model_validate(item) for item in items]


@router.get("/users")
async def users(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[UserAdminResponse]:
    """Return privacy-limited user operations data."""
    items = await _service(session, request, actor).users(limit)
    return [UserAdminResponse.model_validate(item) for item in items]


@router.get("/deliveries")
async def deliveries(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
    actor: AdminPrincipal,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[DeliveryAdminResponse]:
    """Return recent push provider delivery outcomes."""
    items = await _service(session, request, actor).deliveries(limit)
    return [DeliveryAdminResponse.model_validate(item) for item in items]


def _ensure_override_role(actor: User, *, override: bool) -> None:
    if override and actor.role != "admin":
        raise HTTPException(HTTPStatus.FORBIDDEN, ADMIN_OVERRIDE_REQUIRED)
