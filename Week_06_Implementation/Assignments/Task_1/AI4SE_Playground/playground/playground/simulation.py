"""Order simulation and report containers."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from .base import PricingStrategy
from .enums import Category, EventType, OrderStatus
from .events import EventBus
from .exceptions import OutOfStockError
from .inventory import InventoryLedger, Warehouse
from .models import Customer, Money, Product
from .orders import Order, OrderBuilder, OrderLog
from .pricing import FlatPricing
from .repository import InMemoryRepository
from .util import ensure_positive_int, format_cents

_REPORT_KINDS = ("created", "shipped", "cancelled", "rejected")


class SimulationReport:
    """Plain result container for a simulation run."""

    def __init__(self) -> None:
        """Initialise all counters and revenue to zero."""
        self._counts: Dict[str, int] = {kind: 0 for kind in _REPORT_KINDS}
        self._revenue: Money = Money(0)

    @property
    def orders_created(self) -> int:
        """Return the number of orders created."""
        return self._counts["created"]

    @property
    def orders_shipped(self) -> int:
        """Return the number of orders shipped."""
        return self._counts["shipped"]

    @property
    def orders_cancelled(self) -> int:
        """Return the number of orders cancelled."""
        return self._counts["cancelled"]

    @property
    def rejected_out_of_stock(self) -> int:
        """Return the number of steps rejected for insufficient stock."""
        return self._counts["rejected"]

    @property
    def revenue(self) -> Money:
        """Return the total revenue earned by shipped orders."""
        return self._revenue

    def record(self, kind: str) -> None:
        """Increment the counter for ``kind``; raises if the kind is unknown."""
        if kind not in _REPORT_KINDS:
            raise ValueError(f"unknown report kind: {kind!r}")
        self._counts[kind] += 1

    def add_revenue(self, amount: Money) -> None:
        """Add ``amount`` to the total revenue."""
        if not isinstance(amount, Money):
            raise TypeError("amount must be Money")
        self._revenue = self._revenue + amount

    def summary(self) -> Dict[str, object]:
        """Return a dictionary summary of counts and formatted revenue."""
        return {
            "orders_created": self.orders_created,
            "orders_shipped": self.orders_shipped,
            "orders_cancelled": self.orders_cancelled,
            "rejected_out_of_stock": self.rejected_out_of_stock,
            "revenue": format_cents(self._revenue.cents),
        }

    def __str__(self) -> str:
        """Render the summary as one ``key: value`` line per entry."""
        return "\n".join(f"{key}: {value}" for key, value in self.summary().items())


class Simulation:
    """Drives random order activity against a :class:`Warehouse`."""

    def __init__(
        self,
        warehouse: Warehouse,
        pricing: PricingStrategy,
        seed: int = 0,
        bus: Optional[EventBus] = None,
    ) -> None:
        """Create a simulation bound to ``warehouse`` and ``pricing``."""
        if not isinstance(warehouse, Warehouse):
            raise TypeError("warehouse must be Warehouse")
        if not isinstance(pricing, PricingStrategy):
            raise TypeError("pricing must be PricingStrategy")
        self._warehouse = warehouse
        self._pricing = pricing
        self._bus = EventBus() if bus is None else bus
        self._rng = random.Random(seed)
        self._log = OrderLog()
        self._report = SimulationReport()
        self._next_id = 1
        self._customers: List[Customer] = []

    @property
    def log(self) -> OrderLog:
        """Return the order log."""
        return self._log

    @property
    def report(self) -> SimulationReport:
        """Return the simulation report."""
        return self._report

    @property
    def bus(self) -> EventBus:
        """Return the event bus."""
        return self._bus

    def add_customer(self, customer: Customer) -> None:
        """Register a customer for order generation."""
        if not isinstance(customer, Customer):
            raise TypeError("customer must be Customer")
        self._customers.append(customer)

    def step(self) -> Optional[Order]:
        """Run one step of the simulation and return the created order, if any."""
        if not self._customers:
            return None
        customer = self._rng.choice(self._customers)
        skus = sorted(list(self._warehouse.ledger))
        if not skus:
            self._report.record("rejected")
            return None
        sku = self._rng.choice(skus)
        quantity = self._rng.randint(1, 3)

        order_id = f"ORD-{self._next_id:05d}"
        self._next_id += 1
        order = (
            OrderBuilder(customer, self._pricing)
            .add(sku, quantity, Money(1000))
            .build(order_id)
        )

        try:
            reservation = self._warehouse.ledger.reserve(sku, quantity)
        except OutOfStockError:
            self._report.record("rejected")
            return None

        order.advance(OrderStatus.RESERVED)
        self._log.record(order)
        self._report.record("created")
        self._bus.publish(
            EventType.STOCK_RESERVED,
            {"order_id": order.order_id, "sku": sku, "quantity": quantity},
        )

        cancel = self._rng.random() < 0.2
        with reservation:
            if not cancel:
                reservation.commit()

        if cancel:
            order.advance(OrderStatus.CANCELLED)
            self._report.record("cancelled")
            self._bus.publish(
                EventType.ORDER_CANCELLED,
                {"order_id": order.order_id, "sku": sku, "quantity": quantity},
            )
        else:
            order.advance(OrderStatus.SHIPPED)
            self._report.record("shipped")
            self._report.add_revenue(order.total)
            self._bus.publish(
                EventType.ORDER_SHIPPED,
                {"order_id": order.order_id, "sku": sku, "quantity": quantity},
            )
        return order

    def run(self, steps: int) -> SimulationReport:
        """Run ``steps`` steps and return the resulting report."""
        steps = ensure_positive_int(steps, "steps")
        for _ in range(steps):
            self.step()
        return self._report


def build_default_warehouse() -> Warehouse:
    """Create a warehouse stocked with three products (20 units each)."""
    repo = InMemoryRepository(Product)
    repo.add(Product("EL-1001", "Headphones", Category.ELECTRONICS, Money(2500)))
    repo.add(Product("GR-2001", "Coffee Beans", Category.GROCERY, Money(300)))
    repo.add(Product("HW-3001", "Hammer", Category.HARDWARE, Money(1200)))
    ledger = InventoryLedger(repo)
    warehouse = Warehouse("WH-1", "Main", ledger)
    for sku in ("EL-1001", "GR-2001", "HW-3001"):
        warehouse.receive(sku, 20)
    return warehouse


def run_simulation(seed: int, steps: int) -> SimulationReport:
    """Build the default warehouse, then run a seeded simulation for ``steps``."""
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be int")
    steps = ensure_positive_int(steps, "steps")
    warehouse = build_default_warehouse()
    sim = Simulation(warehouse, FlatPricing(tax_bps=800), seed=seed)
    sim.add_customer(Customer("C-1", "Customer One", Money(1000000)))
    sim.add_customer(Customer("C-2", "Customer Two", Money(50000)))
    return sim.run(steps)
