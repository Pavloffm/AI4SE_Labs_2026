"""Inventory ledger and warehouse location."""

from __future__ import annotations

from typing import Dict, Iterator

from .base import Entity, Repository
from .exceptions import InvalidTransitionError, OutOfStockError, UnknownSKUError
from .util import ensure_positive_int, normalize_sku


class InventoryLedger:
    """Tracks on-hand and reserved quantities per SKU."""

    def __init__(self, product_repo: Repository) -> None:
        """Create a ledger backed by ``product_repo`` for SKU validation."""
        if not isinstance(product_repo, Repository):
            raise TypeError("product_repo must be a Repository")
        self._product_repo = product_repo
        self._on_hand: Dict[str, int] = {}
        self._reserved: Dict[str, int] = {}

    def _require_sku(self, sku: str) -> str:
        """Normalise ``sku`` and raise ``UnknownSKUError`` if it is unregistered."""
        sku = normalize_sku(sku)
        if sku not in self._product_repo:
            raise UnknownSKUError(sku)
        return sku

    def add_stock(self, sku: str, quantity: int) -> int:
        """Add ``quantity`` to on-hand stock for ``sku``; return the new total."""
        quantity = ensure_positive_int(quantity, "quantity")
        sku = self._require_sku(sku)
        self._on_hand[sku] = self._on_hand.get(sku, 0) + quantity
        return self._on_hand[sku]

    def available(self, sku: str) -> int:
        """Return on-hand minus reserved for ``sku``."""
        sku = self._require_sku(sku)
        return self._on_hand.get(sku, 0) - self._reserved.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> ReservationContext:
        """Reserve ``quantity`` of ``sku`` and return a context that can commit or release it."""
        quantity = ensure_positive_int(quantity, "quantity")
        sku = self._require_sku(sku)
        avail = self.available(sku)
        if quantity > avail:
            raise OutOfStockError(sku, quantity, avail)
        self._reserved[sku] = self._reserved.get(sku, 0) + quantity
        return ReservationContext(self, sku, quantity)

    def release(self, sku: str, quantity: int) -> None:
        """Release ``quantity`` previously reserved for ``sku``."""
        quantity = ensure_positive_int(quantity, "quantity")
        sku = self._require_sku(sku)
        reserved = self._reserved.get(sku, 0)
        if quantity > reserved:
            raise InvalidTransitionError(reserved, quantity)
        self._reserved[sku] = reserved - quantity

    def commit(self, sku: str, quantity: int) -> None:
        """Commit ``quantity`` of ``sku``: decrement both reserved and on-hand."""
        quantity = ensure_positive_int(quantity, "quantity")
        sku = self._require_sku(sku)
        reserved = self._reserved.get(sku, 0)
        if quantity > reserved:
            raise InvalidTransitionError(reserved, quantity)
        self._reserved[sku] = reserved - quantity
        self._on_hand[sku] = self._on_hand.get(sku, 0) - quantity

    def __contains__(self, sku: object) -> bool:
        """Return whether ``sku`` normalises to a SKU with positive on-hand stock."""
        if not isinstance(sku, str):
            return False
        try:
            sku = normalize_sku(sku)
        except (TypeError, ValueError):
            return False
        return self._on_hand.get(sku, 0) > 0

    def __len__(self) -> int:
        """Return the number of SKUs with positive on-hand stock."""
        return sum(1 for qty in self._on_hand.values() if qty > 0)

    def __iter__(self) -> Iterator[str]:
        """Iterate over SKUs with positive on-hand stock, in sorted order."""
        for sku in sorted(k for k, v in self._on_hand.items() if v > 0):
            yield sku


class ReservationContext:
    """Context manager for a reservation; releases on exit unless committed."""

    def __init__(self, ledger: InventoryLedger, sku: str, quantity: int) -> None:
        """Create a held reservation for ``quantity`` of ``sku`` in ``ledger``."""
        self._ledger = ledger
        self._sku = sku
        self._quantity = quantity
        self._state = "held"

    @property
    def state(self) -> str:
        """Return the current reservation state."""
        return self._state

    def __enter__(self) -> ReservationContext:
        """Enter the context; raises if the reservation is not in the held state."""
        if self._state != "held":
            raise InvalidTransitionError(self._state, "held")
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        """Release the reservation on exit unless it was committed."""
        if self._state == "held":
            self._ledger.release(self._sku, self._quantity)
            self._state = "released"
        return False

    def commit(self) -> None:
        """Commit the reservation, decrementing stock; raises if not held."""
        if self._state != "held":
            raise InvalidTransitionError(self._state, "committed")
        self._ledger.commit(self._sku, self._quantity)
        self._state = "committed"

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"ReservationContext({self._sku!r}, {self._quantity}, {self._state!r})"


class Warehouse(Entity):
    """Named location owning an :class:`InventoryLedger`."""

    def __init__(self, warehouse_id: str, name: str, ledger: InventoryLedger) -> None:
        """Create a warehouse with the given id, name, and ledger."""
        if not isinstance(warehouse_id, str) or warehouse_id.strip() == "":
            raise ValueError("warehouse_id required")
        if not isinstance(ledger, InventoryLedger):
            raise TypeError("ledger must be InventoryLedger")
        self._warehouse_id = warehouse_id
        self._name = name
        self._ledger = ledger

    def identity(self) -> str:
        """Return the warehouse_id as the entity identity."""
        return self._warehouse_id

    @property
    def ledger(self) -> InventoryLedger:
        """Return the warehouse inventory ledger."""
        return self._ledger

    def receive(self, sku: str, quantity: int) -> int:
        """Add stock to the warehouse ledger; return the new on-hand total."""
        return self._ledger.add_stock(sku, quantity)

    def stock_report(self) -> Dict[str, int]:
        """Return a mapping of SKU to available quantity."""
        return {sku: self._ledger.available(sku) for sku in self._ledger}

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Warehouse({self._warehouse_id!r}, {self._name!r})"
