"""Exception hierarchy for the playground package."""

from __future__ import annotations


class PlaygroundError(Exception):
    """Root of the playground exception hierarchy."""

    pass


class InventoryError(PlaygroundError):
    """Generic inventory failure."""

    pass


class OutOfStockError(InventoryError):
    """Requested quantity exceeds available stock."""

    def __init__(self, sku: str, requested: int, available: int) -> None:
        """Store the SKU, requested amount, and available amount."""
        self.sku = sku
        self.requested = requested
        self.available = available
        super().__init__(
            f"insufficient stock for {sku}: requested {requested}, available {available}"
        )


class UnknownSKUError(InventoryError):
    """SKU is not registered in the product repository."""

    def __init__(self, sku: str) -> None:
        """Store the unknown SKU."""
        self.sku = sku
        super().__init__(f"unknown SKU: {sku}")


class DuplicateEntityError(PlaygroundError):
    """Identity already exists in a repository."""

    def __init__(self, key: str) -> None:
        """Store the duplicate identity key."""
        self.key = key
        super().__init__(f"duplicate entity: {key}")


class InvalidTransitionError(PlaygroundError):
    """Illegal status transition or modification of a closed object."""

    def __init__(self, source: object, target: object) -> None:
        """Store the source and target of the invalid transition."""
        self.source = source
        self.target = target
        super().__init__(f"invalid transition: {source!r} -> {target!r}")
