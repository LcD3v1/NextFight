"""Public event and card API contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from nextfight.infrastructure.database.entities import EventStatus, FightStatus


class OrganizationSummary(BaseModel):
    """Organization fields embedded in an event."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    logo_url: str | None


class AthleteSummary(BaseModel):
    """Athlete fields embedded in a fight."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    nickname: str | None
    country_code: str | None
    image_url: str | None


class EventSummary(BaseModel):
    """Event list representation."""

    id: UUID
    name: str
    slug: str
    venue: str | None
    city: str | None
    country_code: str | None
    scheduled_start_at: datetime
    actual_start_at: datetime | None
    status: EventStatus
    organization: OrganizationSummary


class FightResponse(BaseModel):
    """Ordered public fight-card item."""

    id: UUID
    event_id: UUID
    red_athlete: AthleteSummary
    blue_athlete: AthleteSummary
    weight_class: str | None
    bout_type: str | None
    scheduled_order: int
    current_order: int
    rounds_scheduled: int
    status: FightStatus
    actual_start_at: datetime | None
    actual_end_at: datetime | None
    result_method: str | None
    winner_athlete_id: UUID | None


class EventDetail(EventSummary):
    """Event representation including its current ordered card."""

    fights: list[FightResponse]


class EventListResponse(BaseModel):
    """Bounded event collection."""

    items: list[EventSummary]
    has_more: bool
