"""Abstract base classes for entities, pricing, and repositories."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterator, Sequence

if TYPE_CHECKING:
    from .models import LineItem, Money


class Entity(ABC):
    """Anything with a stable identity; equality and hashing derive from it."""

    @abstractmethod
    def identity(self) -> str:
        """Return the unique key for this entity."""

    def __eq__(self, other: object) -> bool:
        """Compare identity for entities of the same concrete type."""
        if type(self) is not type(other):
            return NotImplemented
        return self.identity() == other.identity()

    def __hash__(self) -> int:
        """Hash by the concrete type name and identity."""
        return hash((type(self).__name__, self.identity()))

    def __repr__(self) -> str:
        """Return a developer-friendly representation including the identity."""
        return f"{type(self).__name__}({self.identity()!r})"


class PricingStrategy(ABC):
    """Computes an order total from line items."""

    @abstractmethod
    def price(self, items: Sequence["LineItem"]) -> "Money":
        """Return the total for the given items."""

    def __call__(self, items: Sequence["LineItem"]) -> "Money":
        """Convenience alias for :meth:`price`."""
        return self.price(items)

    @staticmethod
    def _sum_subtotals(items: Sequence["LineItem"]) -> "Money":
        """Sum the subtotal of each item, returning a zero Money for empty input."""
        from .models import Money

        if len(items) == 0:
            return Money(0)
        total = Money(0)
        for item in items:
            total = total + item.subtotal
        return total


class Repository(ABC):
    """Keyed storage of entities."""

    @abstractmethod
    def add(self, item: Entity) -> None:
        """Store an entity keyed by its identity."""

    @abstractmethod
    def get(self, key: str) -> Entity:
        """Return the entity for key; raise KeyError if missing."""

    @abstractmethod
    def remove(self, key: str) -> Entity:
        """Remove and return the entity for key; raise KeyError if missing."""

    @abstractmethod
    def __iter__(self) -> Iterator[Entity]:
        """Iterate over stored entities."""

    def __contains__(self, key: object) -> bool:
        """Return whether ``key`` is a string and its entity is present."""
        if not isinstance(key, str):
            return False
        try:
            self.get(key)
        except KeyError:
            return False
        return True
