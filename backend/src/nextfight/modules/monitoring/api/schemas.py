"""Monitoring timeline and prediction API contracts."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from nextfight.infrastructure.database.entities import FightStatus


class PredictionResponse(BaseModel):
    """Latest transparent start-window prediction."""

    model_config = ConfigDict(from_attributes=True)
    fight_id: UUID
    predicted_start_at: datetime
    earliest_start_at: datetime
    latest_start_at: datetime
    confidence_score: Decimal
    model_version: str
    factors: dict[str, object]
    created_at: datetime


class TimelineItem(BaseModel):
    """Immutable fight state observation."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    fight_id: UUID
    state: FightStatus
    round_number: int | None
    clock_seconds: int | None
    source: str
    occurred_at: datetime
