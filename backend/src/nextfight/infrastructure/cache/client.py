"""Redis client construction."""

from redis.asyncio import Redis

from nextfight.core.config import Settings


def create_redis_client(settings: Settings) -> Redis:
    """Create the process-wide asynchronous Redis client."""
    # redis-py intentionally leaves URL-specific keyword arguments untyped.
    return Redis.from_url(  # pyright: ignore[reportUnknownMemberType]
        settings.redis_url.get_secret_value(),
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
        socket_connect_timeout=settings.health_check_timeout_seconds,
        socket_timeout=settings.health_check_timeout_seconds,
    )
