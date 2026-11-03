"""In-memory repository implementation."""

from __future__ import annotations

from typing import Dict, Iterator

from .base import Entity, Repository
from .exceptions import DuplicateEntityError


class InMemoryRepository(Repository):
    """Dict-backed repository keyed by ``item.identity()``."""

    def __init__(self, entity_type: type) -> None:
        """Create a repository restricted to instances of ``entity_type``."""
        if not isinstance(entity_type, type):
            raise TypeError("entity_type must be a type")
        self._entity_type = entity_type
        self._store: Dict[str, Entity] = {}

    def add(self, item: Entity) -> None:
        """Store ``item`` keyed by its identity; raises on duplicate or wrong type."""
        if not isinstance(item, self._entity_type):
            raise TypeError(f"item must be {self._entity_type.__name__}")
        key = item.identity()
        if key in self._store:
            raise DuplicateEntityError(key)
        self._store[key] = item

    def get(self, key: str) -> Entity:
        """Return the stored entity for ``key``; raises TypeError or KeyError."""
        if not isinstance(key, str):
            raise TypeError("key must be str")
        return self._store[key]

    def remove(self, key: str) -> Entity:
        """Remove and return the entity for ``key``; raises KeyError if missing."""
        if key not in self._store:
            raise KeyError(key)
        return self._store.pop(key)

    def __contains__(self, key: object) -> bool:
        """Return whether ``key`` is a string present in the store."""
        return isinstance(key, str) and key in self._store

    def __len__(self) -> int:
        """Return the number of stored entities."""
        return len(self._store)

    def __iter__(self) -> Iterator[Entity]:
        """Iterate over stored entities in sorted key order."""
        for key in sorted(self._store):
            yield self._store[key]
