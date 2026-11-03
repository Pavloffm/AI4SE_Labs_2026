"""Enumerations used throughout the playground package."""

from __future__ import annotations

from enum import Enum


class Category(Enum):
    """Product categories within the warehouse catalogue."""

    ELECTRONICS = "electronics"
    GROCERY = "grocery"
    APPAREL = "apparel"
    HARDWARE = "hardware"

    @classmethod
    def from_label(cls, label: str) -> "Category":
        """Resolve a category from its lowercase label string.

        Raises:
            TypeError: if ``label`` is not a string.
            ValueError: if no member has a matching value.
        """
        if not isinstance(label, str):
            raise TypeError("category label must be str")
        key = label.strip().lower()
        for member in cls:
            if member.value == key:
                return member
        raise ValueError(f"unknown category: {label!r}")

    def __str__(self) -> str:
        """Return the category's value as its string form."""
        return self.value


class OrderStatus(Enum):
    """Lifecycle stages for an order."""

    NEW = "new"
    RESERVED = "reserved"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """True when the status ends further transitions."""
        return self in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)


class EventType(Enum):
    """Event bus topics published by simulation activity."""

    STOCK_ADDED = 1
    STOCK_RESERVED = 2
    STOCK_RELEASED = 3
    ORDER_SHIPPED = 4
    ORDER_CANCELLED = 5
