"""Transactional outbox dispatcher for Redis realtime channels."""

import asyncio
import json
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from nextfight.core.logging import get_logger
from nextfight.infrastructure.database.entities import OutboxEvent

logger = get_logger(__name__)


class OutboxDispatcher:
    """Publish committed integration events with retry and skip-locked claims."""

    def __init__(self, engine: AsyncEngine, redis: Redis) -> None:
        """Bind dispatcher to durable storage and Redis transport."""
        self._sessions = async_sessionmaker(engine, expire_on_commit=False)
        self._redis = redis

    async def dispatch_batch(self, batch_size: int = 100) -> int:
        """Dispatch one locked batch and return the number successfully published."""
        now = datetime.now(UTC)
        published = 0
        async with self._sessions.begin() as session:
            events = list(
                await session.scalars(
                    select(OutboxEvent)
                    .where(
                        OutboxEvent.status == "pending",
                        OutboxEvent.available_at <= now,
                    )
                    .order_by(OutboxEvent.created_at, OutboxEvent.id)
                    .with_for_update(skip_locked=True)
                    .limit(batch_size)
                )
            )
            for event in events:
                try:
                    envelope = {
                        "id": str(event.id),
                        "type": event.event_type,
                        "topic": event.topic,
                        "data": event.payload,
                        "occurred_at": event.created_at.isoformat(),
                    }
                    await self._redis.publish(  # pyright: ignore[reportUnknownMemberType]
                        f"nextfight:{event.topic}",
                        json.dumps(envelope, separators=(",", ":")),
                    )
                    event.status = "published"
                    event.processed_at = now
                    published += 1
                except Exception as error:  # noqa: BLE001 - transport boundary retries safely.
                    event.attempts += 1
                    event.available_at = now + timedelta(
                        seconds=min(300, 2**event.attempts)
                    )
                    logger.warning(
                        "outbox_publish_failed",
                        outbox_event_id=str(event.id),
                        attempt=event.attempts,
                        error_type=type(error).__name__,
                    )
        return published

    async def run(self, stop: asyncio.Event) -> None:
        """Continuously drain committed events until application shutdown."""
        while not stop.is_set():
            try:
                published = await self.dispatch_batch()
            except Exception as error:  # noqa: BLE001 - worker remains available after outages.
                published = 0
                logger.warning(
                    "outbox_dispatch_unavailable",
                    error_type=type(error).__name__,
                )
            if published == 0:
                try:
                    await asyncio.wait_for(stop.wait(), timeout=0.5)
                except TimeoutError:
                    continue
