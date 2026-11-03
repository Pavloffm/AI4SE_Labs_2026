"""Order state-machine, order aggregates, builder, and log."""

from __future__ import annotations

from typing import Dict, FrozenSet, Iterator, List, Tuple

from .base import PricingStrategy
from .enums import OrderStatus
from .exceptions import DuplicateEntityError, InvalidTransitionError
from .models import Customer, LineItem, Money
from .pricing import FlatPricing


class OrderStateMachine:
    """Legal OrderStatus transitions, data-driven via TRANSITIONS."""

    TRANSITIONS: Dict[OrderStatus, FrozenSet[OrderStatus]] = {
        OrderStatus.NEW: frozenset({OrderStatus.RESERVED, OrderStatus.CANCELLED}),
        OrderStatus.RESERVED: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
        OrderStatus.SHIPPED: frozenset(),
        OrderStatus.CANCELLED: frozenset(),
    }

    @staticmethod
    def allowed_from(status: OrderStatus) -> FrozenSet[OrderStatus]:
        """Return the set of statuses reachable from ``status``."""
        if not isinstance(status, OrderStatus):
            raise TypeError("status must be OrderStatus")
        return OrderStateMachine.TRANSITIONS[status]

    def can_transition(self, source: OrderStatus, target: OrderStatus) -> bool:
        """Return whether ``target`` is reachable from ``source``."""
        return target in OrderStateMachine.allowed_from(source)

    def transition(self, source: OrderStatus, target: OrderStatus) -> OrderStatus:
        """Return ``target`` if the transition is allowed, else raise."""
        if not self.can_transition(source, target):
            raise InvalidTransitionError(source, target)
        return target

    def __call__(self, source: OrderStatus, target: OrderStatus) -> OrderStatus:
        """Convenience alias for :meth:`transition`."""
        return self.transition(source, target)


class Order:
    """Customer order with items, status, and pricing."""

    def __init__(self, order_id: str, customer: Customer, pricing: PricingStrategy) -> None:
        """Create a new order in the NEW status for ``customer``."""
        if not isinstance(order_id, str) or order_id.strip() == "":
            raise ValueError("order_id required")
        if not isinstance(customer, Customer):
            raise TypeError("customer must be Customer")
        if not isinstance(pricing, PricingStrategy):
            raise TypeError("pricing must be PricingStrategy")
        self._order_id = order_id
        self._customer = customer
        self._pricing = pricing
        self._items: List[LineItem] = []
        self._status: OrderStatus = OrderStatus.NEW
        self._machine = OrderStateMachine()

    @property
    def order_id(self) -> str:
        """Return the order identity."""
        return self._order_id

    @property
    def customer(self) -> Customer:
        """Return the owning customer."""
        return self._customer

    @property
    def status(self) -> OrderStatus:
        """Return the current order status."""
        return self._status

    @property
    def items(self) -> Tuple[LineItem, ...]:
        """Return a tuple copy of the order's line items."""
        return tuple(self._items)

    @property
    def total(self) -> Money:
        """Return the total price of all line items under this order's pricing."""
        return self._pricing.price(self._items)

    def add_item(self, item: LineItem) -> None:
        """Append ``item``, merging with an existing line for the same SKU."""
        if not isinstance(item, LineItem):
            raise TypeError("item must be LineItem")
        if self._status is not OrderStatus.NEW:
            raise InvalidTransitionError(self._status, OrderStatus.NEW)
        for index, existing in enumerate(self._items):
            if existing.sku == item.sku:
                self._items[index] = existing.with_quantity(existing.quantity + item.quantity)
                return
        self._items.append(item)

    def advance(self, target: OrderStatus) -> None:
        """Transition the order to ``target`` status, raising if not allowed."""
        new_status = self._machine.transition(self._status, target)
        self._status = new_status

    def __len__(self) -> int:
        """Return the number of line items."""
        return len(self._items)

    def __iter__(self) -> Iterator[LineItem]:
        """Iterate over a tuple snapshot of the order's line items."""
        return iter(tuple(self._items))

    def __eq__(self, other: object) -> bool:
        """Compare orders by identity."""
        if not isinstance(other, Order):
            return NotImplemented
        return self._order_id == other._order_id

    def __hash__(self) -> int:
        """Hash by type name and order id."""
        return hash(("Order", self._order_id))

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Order({self._order_id!r}, {self._status.value})"


class OrderBuilder:
    """Fluent construction of an :class:`Order`."""

    def __init__(self, customer: Customer, pricing: PricingStrategy) -> None:
        """Create a builder for ``customer`` and ``pricing``."""
        if not isinstance(customer, Customer):
            raise TypeError("customer must be Customer")
        if not isinstance(pricing, PricingStrategy):
            raise TypeError("pricing must be PricingStrategy")
        self._customer = customer
        self._pricing = pricing
        self._lines: List[Tuple[str, int, Money]] = []

    @classmethod
    def for_customer(cls, customer: Customer) -> OrderBuilder:
        """Create a builder with default :class:`FlatPricing` for ``customer``."""
        return cls(customer, FlatPricing())

    def add(self, sku: str, quantity: int, unit_price: Money) -> OrderBuilder:
        """Record a line item and return self for chaining."""
        item = LineItem(sku, quantity, unit_price)
        self._lines.append((item.sku, item.quantity, item.unit_price))
        return self

    def build(self, order_id: str) -> Order:
        """Construct and return the order; raises if no lines were recorded."""
        if len(self._lines) == 0:
            raise ValueError("no items")
        order = Order(order_id, self._customer, self._pricing)
        for sku, quantity, unit_price in self._lines:
            order.add_item(LineItem(sku, quantity, unit_price))
        return order

    def __len__(self) -> int:
        """Return the number of recorded lines."""
        return len(self._lines)

    def __bool__(self) -> bool:
        """Return True when at least one line has been recorded."""
        return len(self) > 0


class OrderLog:
    """Ordered, deduplicated record of orders; iterable."""

    def __init__(self) -> None:
        """Create an empty order log."""
        self._orders: List[Order] = []

    def record(self, order: Order) -> None:
        """Append ``order``; raises if an order with the same id is already logged."""
        if not isinstance(order, Order):
            raise TypeError("order must be Order")
        for existing in self._orders:
            if existing.order_id == order.order_id:
                raise DuplicateEntityError(order.order_id)
        self._orders.append(order)

    def by_status(self, status: OrderStatus) -> Iterator[Order]:
        """Yield orders whose status matches ``status``."""
        if not isinstance(status, OrderStatus):
            raise TypeError("status must be OrderStatus")
        yield from (order for order in self._orders if order.status is status)

    def __getitem__(self, index: int) -> Order:
        """Return the order at ``index``."""
        return self._orders[index]

    def __len__(self) -> int:
        """Return the number of logged orders."""
        return len(self._orders)

    def __iter__(self) -> Iterator[Order]:
        """Iterate over the logged orders."""
        yield from list(self._orders)
