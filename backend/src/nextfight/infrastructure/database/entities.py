"""Initial persistent entities defined by the product data model."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from nextfight.infrastructure.database.models import Base, EntityMixin


class EventStatus(StrEnum):
    """Allowed event lifecycle states."""

    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    LIVE = "live"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FightStatus(StrEnum):
    """Allowed fight lifecycle states."""

    SCHEDULED = "scheduled"
    NEXT = "next"
    WALKOUTS = "walkouts"
    LIVE = "live"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_CONTEST = "no_contest"


class User(EntityMixin, Base):
    """Registered platform user."""

    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str] = mapped_column(String(120))
    locale: Mapped[str] = mapped_column(String(16), default="en")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    status: Mapped[str] = mapped_column(String(32), index=True)
    role: Mapped[str] = mapped_column(String(32), default="user", index=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshSession(EntityMixin, Base):
    """Rotating and revocable refresh-token session."""

    __tablename__ = "refresh_sessions"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    family_id: Mapped[UUID] = mapped_column(index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("refresh_sessions.id")
    )
    user_agent: Mapped[str | None] = mapped_column(String(512))
    ip_address: Mapped[str | None] = mapped_column(String(45))


class OneTimeToken(EntityMixin, Base):
    """Hashed single-use token for email verification or password reset."""

    __tablename__ = "one_time_tokens"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    purpose: Mapped[str] = mapped_column(String(32), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Device(EntityMixin, Base):
    """Push-capable user device."""

    __tablename__ = "devices"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[str] = mapped_column(String(16))
    push_token: Mapped[str] = mapped_column(Text, unique=True)
    app_version: Mapped[str] = mapped_column(String(32))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Favorite(EntityMixin, Base):
    """User bookmark for a supported public domain entity."""

    __tablename__ = "favorites"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    target_type: Mapped[str] = mapped_column(String(32), index=True)
    target_id: Mapped[UUID] = mapped_column(index=True)
    __table_args__ = (
        CheckConstraint(
            "target_type IN ('event', 'organization', 'athlete')",
            name="favorite_target_type",
        ),
        UniqueConstraint("user_id", "target_type", "target_id"),
    )


class Organization(EntityMixin, Base):
    """Combat sports organization."""

    __tablename__ = "organizations"
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class Athlete(EntityMixin, Base):
    """Combat sports athlete."""

    __tablename__ = "athletes"
    name: Mapped[str] = mapped_column(String(160), index=True)
    nickname: Mapped[str | None] = mapped_column(String(160))
    country_code: Mapped[str | None] = mapped_column(String(2))
    image_url: Mapped[str | None] = mapped_column(Text)
    external_ids: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class Event(EntityMixin, Base):
    """Scheduled or live combat event."""

    __tablename__ = "events"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    venue: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(120))
    country_code: Mapped[str | None] = mapped_column(String(2))
    scheduled_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True
    )
    actual_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(
        SqlEnum(EventStatus, name="event_status"), index=True
    )
    provider_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)


class Fight(EntityMixin, Base):
    """Ordered bout within an event."""

    __tablename__ = "fights"
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), index=True)
    red_athlete_id: Mapped[UUID] = mapped_column(ForeignKey("athletes.id"))
    blue_athlete_id: Mapped[UUID] = mapped_column(ForeignKey("athletes.id"))
    weight_class: Mapped[str | None] = mapped_column(String(80))
    bout_type: Mapped[str | None] = mapped_column(String(80))
    scheduled_order: Mapped[int] = mapped_column(Integer)
    current_order: Mapped[int] = mapped_column(Integer, index=True)
    rounds_scheduled: Mapped[int] = mapped_column(Integer)
    status: Mapped[FightStatus] = mapped_column(
        SqlEnum(FightStatus, name="fight_status"), index=True
    )
    actual_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_method: Mapped[str | None] = mapped_column(String(120))
    winner_athlete_id: Mapped[UUID | None] = mapped_column(ForeignKey("athletes.id"))
    provider_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    __table_args__ = (UniqueConstraint("event_id", "current_order"),)


class Alert(EntityMixin, Base):
    """User-configured fight alert."""

    __tablename__ = "alerts"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    fight_id: Mapped[UUID] = mapped_column(ForeignKey("fights.id"), index=True)
    trigger_type: Mapped[str] = mapped_column(String(64))
    lead_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), index=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        Index("ix_alerts_fight_status", "fight_id", "status"),
        UniqueConstraint("user_id", "fight_id", "trigger_type", "lead_minutes"),
    )


class FightStateEvent(EntityMixin, Base):
    """Immutable observation in a fight timeline."""

    __tablename__ = "fight_state_events"
    fight_id: Mapped[UUID] = mapped_column(ForeignKey("fights.id"), index=True)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), index=True)
    state: Mapped[FightStatus] = mapped_column(
        SqlEnum(FightStatus, name="fight_status", create_type=False)
    )
    round_number: Mapped[int | None] = mapped_column(Integer)
    clock_seconds: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(160), unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class AlertDelivery(EntityMixin, Base):
    """Idempotent attempt to deliver an alert."""

    __tablename__ = "alert_deliveries"
    alert_id: Mapped[UUID] = mapped_column(ForeignKey("alerts.id"), index=True)
    device_id: Mapped[UUID] = mapped_column(ForeignKey("devices.id"), index=True)
    channel: Mapped[str] = mapped_column(String(32))
    idempotency_key: Mapped[str] = mapped_column(String(160), unique=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(80))


class Prediction(EntityMixin, Base):
    """Versioned prediction for a fight start window."""

    __tablename__ = "predictions"
    fight_id: Mapped[UUID] = mapped_column(ForeignKey("fights.id"), index=True)
    predicted_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    earliest_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latest_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    model_version: Mapped[str] = mapped_column(String(64))
    factors: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1", name="confidence_range"
        ),
    )


class EventChange(EntityMixin, Base):
    """Auditable event or card mutation."""

    __tablename__ = "event_changes"
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[UUID] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(String(64))
    before_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(String(64))
    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))


class OutboxEvent(EntityMixin, Base):
    """Transactional integration event awaiting reliable publication."""

    __tablename__ = "outbox_events"
    topic: Mapped[str] = mapped_column(String(160), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Subscription(EntityMixin, Base):
    """User billing subscription reference."""

    __tablename__ = "subscriptions"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    plan: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    external_customer_id: Mapped[str] = mapped_column(String(160))
    external_subscription_id: Mapped[str] = mapped_column(String(160), unique=True)


class AuditLog(EntityMixin, Base):
    """Immutable record of a sensitive administrative action."""

    __tablename__ = "audit_logs"
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[UUID | None] = mapped_column(index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    changes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
