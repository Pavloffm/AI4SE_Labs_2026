"""Warehouse inventory and order processing playground."""

from __future__ import annotations

__version__ = "0.1.0"

from .decorators import AuditTrail
from .enums import Category, EventType, OrderStatus
from .events import EventBus
from .exceptions import (
    DuplicateEntityError,
    InvalidTransitionError,
    InventoryError,
    OutOfStockError,
    PlaygroundError,
    UnknownSKUError,
)
from .inventory import Warehouse
from .models import Customer, LineItem, Money, Product
from .orders import Order, OrderBuilder, OrderLog
from .pricing import BulkDiscountPricing, FlatPricing
from .simulation import Simulation, run_simulation

__all__ = [
    "__version__",
    "Money",
    "Product",
    "LineItem",
    "Customer",
    "Warehouse",
    "Order",
    "OrderBuilder",
    "OrderLog",
    "FlatPricing",
    "BulkDiscountPricing",
    "EventBus",
    "AuditTrail",
    "Simulation",
    "PlaygroundError",
    "InventoryError",
    "OutOfStockError",
    "UnknownSKUError",
    "DuplicateEntityError",
    "InvalidTransitionError",
    "Category",
    "OrderStatus",
    "EventType",
    "run_simulation",
]
