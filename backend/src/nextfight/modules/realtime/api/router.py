"""Authenticated Redis-backed WebSocket subscriptions."""

import asyncio
from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker

from nextfight.infrastructure.database.entities import User
from nextfight.modules.identity.domain.security import (
    InvalidAccessTokenError,
    TokenService,
)

router = APIRouter(tags=["Realtime"])
AUTH_TIMEOUT_SECONDS = 10


class AuthenticationMessage(BaseModel):
    """Initial WebSocket authentication and subscription request."""

    model_config = ConfigDict(extra="forbid")
    type: str = Field(pattern="^authenticate$")
    access_token: str = Field(min_length=20, max_length=4096)
    topics: list[str] = Field(default_factory=list, max_length=100)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Authenticate, authorize topics, and stream realtime envelopes."""
    await websocket.accept()
    pubsub = websocket.app.state.redis.pubsub()
    try:
        raw = await asyncio.wait_for(
            websocket.receive_json(), timeout=AUTH_TIMEOUT_SECONDS
        )
        authentication = AuthenticationMessage.model_validate(raw)
        claims = TokenService(websocket.app.state.settings).decode_access_token(
            authentication.access_token
        )
        sessions = async_sessionmaker(
            websocket.app.state.database_engine, expire_on_commit=False
        )
        async with sessions() as session:
            user = await session.get(User, claims.subject)
        if user is None or user.status != "active" or user.role != claims.role:
            await websocket.close(code=HTTPStatus.UNAUTHORIZED + 4000)
            return
        topics = authorize_topics(authentication.topics, user.id)
        if topics:
            await pubsub.subscribe(*(f"nextfight:{topic}" for topic in topics))
        await websocket.send_json(
            {"type": "connection.ready", "topics": sorted(topics)}
        )
        while True:
            message: dict[str, Any] | None = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message is not None and isinstance(message.get("data"), str):
                await websocket.send_text(message["data"])
            else:
                await websocket.send_json({"type": "connection.keepalive"})
    except (InvalidAccessTokenError, ValidationError, TimeoutError):
        await websocket.close(code=HTTPStatus.UNAUTHORIZED + 4000)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.aclose()


def authorize_topics(requested: list[str], user_id: UUID) -> set[str]:
    """Allow public aggregate topics and only the principal's private topic."""
    allowed: set[str] = set()
    private_topic = f"user:{user_id}"
    for topic in requested:
        prefix, separator, identifier = topic.partition(":")
        if separator != ":":
            continue
        if prefix in {"event", "fight"}:
            try:
                UUID(identifier)
            except ValueError:
                continue
            allowed.add(topic)
        elif topic == private_topic:
            allowed.add(topic)
    return allowed
