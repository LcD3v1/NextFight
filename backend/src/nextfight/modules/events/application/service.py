"""Read use cases for events and current fight cards."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from nextfight.infrastructure.database.entities import (
    Athlete,
    Event,
    EventStatus,
    Fight,
    Organization,
)
from nextfight.modules.events.api.schemas import (
    AthleteSummary,
    EventDetail,
    EventListResponse,
    EventSummary,
    FightResponse,
    OrganizationSummary,
)


class EventNotFoundError(LookupError):
    """Raised when a public event or fight does not exist."""


class EventQueryService:
    """Load public event projections without exposing persistence entities."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind queries to the request transaction."""
        self._session = session

    async def list_events(
        self, *, statuses: tuple[EventStatus, ...], limit: int
    ) -> EventListResponse:
        """List chronological events filtered by lifecycle status."""
        rows = (
            await self._session.execute(
                select(Event, Organization)
                .join(Organization, Organization.id == Event.organization_id)
                .where(Event.status.in_(statuses))
                .order_by(Event.scheduled_start_at, Event.id)
                .limit(limit + 1)
            )
        ).all()
        return EventListResponse(
            items=[
                self._event(event, organization) for event, organization in rows[:limit]
            ],
            has_more=len(rows) > limit,
        )

    async def get_event(self, event_id: UUID) -> EventDetail:
        """Load one event and its latest ordered fight card."""
        row = (
            await self._session.execute(
                select(Event, Organization)
                .join(Organization, Organization.id == Event.organization_id)
                .where(Event.id == event_id)
            )
        ).one_or_none()
        if row is None:
            raise EventNotFoundError
        event, organization = row
        summary = self._event(event, organization)
        return EventDetail(
            **summary.model_dump(), fights=await self.list_fights(event_id)
        )

    async def list_fights(self, event_id: UUID) -> list[FightResponse]:
        """Load an event's card in its operator-controlled current order."""
        red = aliased(Athlete)
        blue = aliased(Athlete)
        rows = (
            await self._session.execute(
                select(Fight, red, blue)
                .join(red, red.id == Fight.red_athlete_id)
                .join(blue, blue.id == Fight.blue_athlete_id)
                .where(Fight.event_id == event_id)
                .order_by(Fight.current_order, Fight.id)
            )
        ).all()
        return [
            self._fight(fight, red_athlete, blue_athlete)
            for fight, red_athlete, blue_athlete in rows
        ]

    @staticmethod
    def _event(event: Event, organization: Organization) -> EventSummary:
        return EventSummary(
            id=event.id,
            name=event.name,
            slug=event.slug,
            venue=event.venue,
            city=event.city,
            country_code=event.country_code,
            scheduled_start_at=event.scheduled_start_at,
            actual_start_at=event.actual_start_at,
            status=event.status,
            organization=OrganizationSummary.model_validate(organization),
        )

    @staticmethod
    def _fight(fight: Fight, red: Athlete, blue: Athlete) -> FightResponse:
        return FightResponse(
            id=fight.id,
            event_id=fight.event_id,
            red_athlete=AthleteSummary.model_validate(red),
            blue_athlete=AthleteSummary.model_validate(blue),
            weight_class=fight.weight_class,
            bout_type=fight.bout_type,
            scheduled_order=fight.scheduled_order,
            current_order=fight.current_order,
            rounds_scheduled=fight.rounds_scheduled,
            status=fight.status,
            actual_start_at=fight.actual_start_at,
            actual_end_at=fight.actual_end_at,
            result_method=fight.result_method,
            winner_athlete_id=fight.winner_athlete_id,
        )
