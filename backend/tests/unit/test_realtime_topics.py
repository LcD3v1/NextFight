"""Realtime topic authorization tests."""

from uuid import uuid4

from nextfight.modules.realtime.api.router import authorize_topics


def test_topic_authorization_limits_private_channels() -> None:
    """Allow valid aggregate topics and only the principal's private topic."""
    user_id = uuid4()
    event_id = uuid4()
    allowed = authorize_topics(
        [
            f"event:{event_id}",
            f"fight:{uuid4()}",
            f"user:{user_id}",
            f"user:{uuid4()}",
            "event:not-a-uuid",
            "invalid",
        ],
        user_id,
    )
    assert f"event:{event_id}" in allowed
    assert f"user:{user_id}" in allowed
    assert len(allowed) == 3  # noqa: PLR2004
