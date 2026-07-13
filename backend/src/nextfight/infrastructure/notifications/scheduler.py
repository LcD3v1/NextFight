"""Prediction-aware lead-time alert scheduler."""

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from nextfight.core.logging import get_logger
from nextfight.infrastructure.database.entities import (
    Alert,
    AlertDelivery,
    Device,
    Fight,
    FightStatus,
    Prediction,
    User,
)
from nextfight.infrastructure.notifications.messages import localized_lead_message

logger = get_logger(__name__)
MAX_LEAD_MINUTES = 120


class LeadTimeAlertScheduler:
    """Convert due fight predictions into idempotent device deliveries."""

    def __init__(self, engine: AsyncEngine) -> None:
        """Bind the scheduler to durable PostgreSQL storage."""
        self._sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def schedule_due(self, batch_size: int = 1000) -> int:
        """Schedule due lead-time alerts and return newly inserted deliveries."""
        now = datetime.now(UTC)
        latest_prediction_id = (
            select(Prediction.id)
            .where(Prediction.fight_id == Fight.id)
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .limit(1)
            .correlate(Fight)
            .scalar_subquery()
        )
        async with self._sessions.begin() as session:
            rows = (
                await session.execute(
                    select(Alert, Device, User, Fight, Prediction)
                    .join(Device, Device.user_id == Alert.user_id)
                    .join(User, User.id == Alert.user_id)
                    .join(Fight, Fight.id == Alert.fight_id)
                    .join(Prediction, Prediction.id == latest_prediction_id)
                    .where(
                        Alert.trigger_type == "lead_time",
                        Alert.status == "active",
                        Alert.lead_minutes.is_not(None),
                        Device.notifications_enabled.is_(True),
                        Fight.status.in_(
                            (
                                FightStatus.SCHEDULED,
                                FightStatus.NEXT,
                                FightStatus.WALKOUTS,
                            )
                        ),
                        Prediction.predicted_start_at
                        <= now + timedelta(minutes=MAX_LEAD_MINUTES),
                    )
                    .limit(batch_size)
                )
            ).all()
            inserted = 0
            for alert, device, user, fight, prediction in rows:
                minutes = alert.lead_minutes
                if minutes is None or prediction.predicted_start_at > now + timedelta(
                    minutes=minutes
                ):
                    continue
                title, body = localized_lead_message(user.locale, minutes)
                statement = (
                    insert(AlertDelivery)
                    .values(
                        alert_id=alert.id,
                        device_id=device.id,
                        channel="push",
                        idempotency_key=f"alert:lead:{alert.id}:{device.id}",
                        status="pending",
                        title=title,
                        body=body,
                        data={
                            "type": "fight.lead_time",
                            "fight_id": str(fight.id),
                            "event_id": str(fight.event_id),
                            "lead_minutes": str(minutes),
                        },
                        attempts=0,
                        next_attempt_at=now,
                    )
                    .on_conflict_do_nothing(index_elements=["idempotency_key"])
                    .returning(AlertDelivery.id)
                )
                if await session.scalar(statement) is not None:
                    inserted += 1
            return inserted

    async def run(self, stop: asyncio.Event) -> None:
        """Poll predictions until graceful application shutdown."""
        while not stop.is_set():
            try:
                await self.schedule_due()
            except Exception as error:  # noqa: BLE001 - scheduler survives outages.
                logger.warning(
                    "lead_time_scheduler_unavailable",
                    error_type=type(error).__name__,
                )
            try:
                await asyncio.wait_for(stop.wait(), timeout=15)
            except TimeoutError:
                continue
