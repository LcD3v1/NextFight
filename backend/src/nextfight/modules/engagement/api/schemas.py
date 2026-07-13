"""Favorites, alerts, and devices API contracts."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

FavoriteTarget = Literal["event", "organization", "athlete"]
AlertTrigger = Literal["lead_time", "next_fight", "walkouts"]
AlertStatus = Literal["active", "paused"]
DevicePlatform = Literal["android", "ios"]


class FavoriteCreate(BaseModel):
    """Favorite creation input."""

    model_config = ConfigDict(extra="forbid")
    target_type: FavoriteTarget
    target_id: UUID


class FavoriteResponse(BaseModel):
    """Persisted favorite representation."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    target_type: FavoriteTarget
    target_id: UUID
    created_at: datetime


class AlertCreate(BaseModel):
    """Fight alert creation input."""

    model_config = ConfigDict(extra="forbid")
    fight_id: UUID
    trigger_type: AlertTrigger
    lead_minutes: int | None = Field(default=None, ge=0, le=120)


class AlertUpdate(BaseModel):
    """Mutable alert preferences."""

    model_config = ConfigDict(extra="forbid")
    status: AlertStatus | None = None
    lead_minutes: int | None = Field(default=None, ge=0, le=120)


class AlertResponse(BaseModel):
    """Persisted alert representation."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    fight_id: UUID
    trigger_type: AlertTrigger
    lead_minutes: int | None
    status: str
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeviceCreate(BaseModel):
    """Push device registration input."""

    model_config = ConfigDict(extra="forbid")
    platform: DevicePlatform
    push_token: str = Field(min_length=16, max_length=4096)
    app_version: str = Field(min_length=1, max_length=32)
    notifications_enabled: bool = True


class DeviceResponse(BaseModel):
    """Push device representation without its provider credential."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    platform: DevicePlatform
    app_version: str
    notifications_enabled: bool
    last_seen_at: datetime
