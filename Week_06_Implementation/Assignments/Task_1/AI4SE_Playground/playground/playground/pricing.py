"""Pricing strategies for computing order totals."""

from __future__ import annotations

from typing import Sequence

from .base import PricingStrategy
from .models import LineItem, Money
from .util import ensure_positive_int


class FlatPricing(PricingStrategy):
    """Sum of subtotals plus flat tax in basis points."""

    def __init__(self, tax_bps: int = 0) -> None:
        """Create a pricing strategy with a tax rate in ``tax_bps`` basis points."""
        if isinstance(tax_bps, bool) or not isinstance(tax_bps, int):
            raise TypeError("tax_bps must be int")
        if tax_bps < 0 or tax_bps > 10000:
            raise ValueError("tax_bps must be 0..10000")
        self._tax_bps = tax_bps

    @property
    def tax_bps(self) -> int:
        """Return the tax rate in basis points."""
        return self._tax_bps

    def price(self, items: Sequence[LineItem]) -> Money:
        """Return the subtotal plus the configured flat tax."""
        subtotal = self._sum_subtotals(items)
        if self._tax_bps == 0:
            return subtotal
        tax = Money(subtotal.cents * self._tax_bps // 10000)
        return subtotal + tax


class BulkDiscountPricing(PricingStrategy):
    """Wraps another strategy; applies a percent discount when total quantity meets a threshold."""

    def __init__(self, base: PricingStrategy, threshold: int, percent_off: int) -> None:
        """Create a strategy that discounts ``base`` totals above ``threshold`` quantity."""
        if not isinstance(base, PricingStrategy):
            raise TypeError("base must be PricingStrategy")
        threshold = ensure_positive_int(threshold, "threshold")
        if isinstance(percent_off, bool) or not isinstance(percent_off, int):
            raise TypeError("percent_off must be int")
        if percent_off < 0 or percent_off > 100:
            raise ValueError("percent_off must be 0..100")
        self._base = base
        self._threshold = threshold
        self._percent_off = percent_off

    @property
    def threshold(self) -> int:
        """Return the qualifying total quantity."""
        return self._threshold

    @property
    def percent_off(self) -> int:
        """Return the discount percentage."""
        return self._percent_off

    def price(self, items: Sequence[LineItem]) -> Money:
        """Return the base price, less the discount if the quantity qualifies."""
        total = self._base.price(items)
        quantity = sum(item.quantity for item in items)
        if quantity < self._threshold:
            return total
        discount = total.cents * self._percent_off // 100
        return Money(total.cents - discount)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"BulkDiscountPricing(threshold={self._threshold}, percent_off={self._percent_off})"
