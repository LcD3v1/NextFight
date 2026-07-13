"""Typed administrative command and query contracts."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from nextfight.infrastructure.database.entities import EventStatus, FightStatus


class OrganizationCreate(BaseModel):
    """Organization creation command."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    logo_url: str | None = None


class AthleteCreate(BaseModel):
    """Athlete creation command."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=160)
    nickname: str | None = Field(default=None, max_length=160)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    image_url: str | None = None


class EventCreate(BaseModel):
    """Event creation command."""

    model_config = ConfigDict(extra="forbid")
    organization_id: UUID
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=200)
    venue: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, max_length=120)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    scheduled_start_at: datetime


class EventUpdate(BaseModel):
    """Mutable event fields."""

    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=2, max_length=200)
    venue: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, max_length=120)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    scheduled_start_at: datetime | None = None


class FightCreate(BaseModel):
    """Fight creation command."""

    model_config = ConfigDict(extra="forbid")
    event_id: UUID
    red_athlete_id: UUID
    blue_athlete_id: UUID
    weight_class: str | None = Field(default=None, max_length=80)
    bout_type: str | None = Field(default=None, max_length=80)
    current_order: int = Field(ge=1, le=100)
    rounds_scheduled: int = Field(ge=1, le=12)


class FightUpdate(BaseModel):
    """Mutable fight metadata."""

    model_config = ConfigDict(extra="forbid")
    weight_class: str | None = Field(default=None, max_length=80)
    bout_type: str | None = Field(default=None, max_length=80)
    rounds_scheduled: int | None = Field(default=None, ge=1, le=12)
    result_method: str | None = Field(default=None, max_length=120)
    winner_athlete_id: UUID | None = None


class FightStateCommand(BaseModel):
    """Audited manual fight-state observation."""

    model_config = ConfigDict(extra="forbid")
    state: FightStatus
    idempotency_key: str = Field(min_length=8, max_length=160)
    occurred_at: datetime
    round_number: int | None = Field(default=None, ge=1, le=12)
    clock_seconds: int | None = Field(default=None, ge=0, le=3600)
    override: bool = False


class EventStateCommand(BaseModel):
    """Audited manual event-state transition."""

    model_config = ConfigDict(extra="forbid")
    state: EventStatus
    idempotency_key: str = Field(min_length=8, max_length=160)
    override: bool = False


class CardOrderCommand(BaseModel):
    """Complete ordered fight identifiers for an event card."""

    model_config = ConfigDict(extra="forbid")
    fight_ids: list[UUID] = Field(min_length=1, max_length=100)


class EntityResponse(BaseModel):
    """Generic typed identifier returned after administrative mutations."""

    id: UUID
    version: int | None = None


class DashboardResponse(BaseModel):
    """Operational dashboard counters."""

    live_events: int
    active_users: int
    pending_deliveries: int
    failed_deliveries: int


class AuditLogResponse(BaseModel):
    """Immutable administrative audit entry."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    actor_user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID | None
    ip_address: str | None
    changes: dict[str, Any]
    created_at: datetime


class OrganizationAdminResponse(BaseModel):
    """Organization catalog row."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    active: bool


class AthleteAdminResponse(BaseModel):
    """Athlete catalog row."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    nickname: str | None
    country_code: str | None


class UserAdminResponse(BaseModel):
    """Privacy-limited user operations row."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    display_name: str
    locale: str
    timezone: str
    status: str
    role: str
    created_at: datetime


class DeliveryAdminResponse(BaseModel):
    """Alert delivery diagnostic row without device credentials."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    alert_id: UUID
    device_id: UUID
    status: str
    attempts: int
    provider_message_id: str | None
    error_code: str | None
    attempted_at: datetime | None
    created_at: datetime
