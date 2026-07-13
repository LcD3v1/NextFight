"""Typed asynchronous repository contracts and SQLAlchemy adapter."""

from typing import Protocol, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from nextfight.infrastructure.database.models import Base

EntityT = TypeVar("EntityT", bound=Base)


class Repository(Protocol[EntityT]):
    """Minimal persistence contract owned by application use cases."""

    async def get(self, entity_id: UUID) -> EntityT | None:
        """Load an entity by public identifier."""
        ...

    async def add(self, entity: EntityT) -> EntityT:
        """Stage and flush a new entity in the current transaction."""
        ...


class SqlAlchemyRepository[EntityT: Base]:
    """Unit-of-work-aware SQLAlchemy repository adapter."""

    def __init__(self, session: AsyncSession, model: type[EntityT]) -> None:
        """Bind the adapter to a transaction and mapped entity type."""
        self._session = session
        self._model = model

    async def get(self, entity_id: UUID) -> EntityT | None:
        """Load an entity from the session identity map or database."""
        return await self._session.get(self._model, entity_id)

    async def add(self, entity: EntityT) -> EntityT:
        """Stage and flush an entity without committing the transaction."""
        self._session.add(entity)
        await self._session.flush()
        return entity
