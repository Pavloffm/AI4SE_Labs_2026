"""Unit tests for the pricing module."""
from __future__ import annotations

import unittest

from playground.base import PricingStrategy
from playground.models import LineItem, Money
from playground.pricing import BulkDiscountPricing, FlatPricing


class FlatPricingConstructionTests(unittest.TestCase):
    def test_default_tax_is_zero(self) -> None:
        self.assertEqual(FlatPricing().tax_bps, 0)

    def test_stores_tax(self) -> None:
        self.assertEqual(FlatPricing(800).tax_bps, 800)

    def test_boundaries_accepted(self) -> None:
        self.assertEqual(FlatPricing(0).tax_bps, 0)
        self.assertEqual(FlatPricing(10000).tax_bps, 10000)

    def test_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            FlatPricing(True)  # type: ignore[arg-type]

    def test_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            FlatPricing(5.0)  # type: ignore[arg-type]

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FlatPricing(-1)

    def test_above_max_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FlatPricing(10001)

    def test_is_pricing_strategy(self) -> None:
        self.assertIsInstance(FlatPricing(), PricingStrategy)


class FlatPricingPriceTests(unittest.TestCase):
    def test_empty_items_zero_tax_is_zero(self) -> None:
        self.assertEqual(FlatPricing().price([]), Money(0))

    def test_empty_items_with_tax_is_zero(self) -> None:
        self.assertEqual(FlatPricing(800).price([]), Money(0))

    def test_zero_tax_returns_subtotal(self) -> None:
        items = [LineItem("EL-1001", 2, Money(250)), LineItem("GR-2001", 1, Money(300))]
        self.assertEqual(FlatPricing().price(items), Money(800))

    def test_tax_applied_with_floor_division(self) -> None:
        # 1000 cents * 800 bps / 10000 = 80 cents tax
        items = [LineItem("EL-1001", 1, Money(1000))]
        self.assertEqual(FlatPricing(800).price(items), Money(1080))

    def test_tax_rounds_down(self) -> None:
        # 333 * 100 // 10000 = 3 (floor of 3.33)
        items = [LineItem("EL-1001", 1, Money(333))]
        self.assertEqual(FlatPricing(100).price(items), Money(336))

    def test_full_tax_doubles_amount(self) -> None:
        items = [LineItem("EL-1001", 1, Money(500))]
        self.assertEqual(FlatPricing(10000).price(items), Money(1000))

    def test_call_matches_price(self) -> None:
        items = [LineItem("EL-1001", 1, Money(500))]
        strategy = FlatPricing(800)
        self.assertEqual(strategy(items), strategy.price(items))


class BulkDiscountConstructionTests(unittest.TestCase):
    def test_stores_fields(self) -> None:
        base = FlatPricing()
        d = BulkDiscountPricing(base, 5, 10)
        self.assertEqual(d.threshold, 5)
        self.assertEqual(d.percent_off, 10)

    def test_base_must_be_strategy(self) -> None:
        with self.assertRaises(TypeError):
            BulkDiscountPricing(object(), 5, 10)  # type: ignore[arg-type]

    def test_threshold_validated(self) -> None:
        with self.assertRaises(ValueError):
            BulkDiscountPricing(FlatPricing(), 0, 10)
        with self.assertRaises(TypeError):
            BulkDiscountPricing(FlatPricing(), True, 10)  # type: ignore[arg-type]

    def test_percent_off_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            BulkDiscountPricing(FlatPricing(), 1, False)  # type: ignore[arg-type]

    def test_percent_off_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            BulkDiscountPricing(FlatPricing(), 1, 5.0)  # type: ignore[arg-type]

    def test_percent_off_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BulkDiscountPricing(FlatPricing(), 1, -1)

    def test_percent_off_above_100_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BulkDiscountPricing(FlatPricing(), 1, 101)

    def test_percent_off_boundaries_accepted(self) -> None:
        self.assertEqual(BulkDiscountPricing(FlatPricing(), 1, 0).percent_off, 0)
        self.assertEqual(BulkDiscountPricing(FlatPricing(), 1, 100).percent_off, 100)

    def test_repr(self) -> None:
        d = BulkDiscountPricing(FlatPricing(), 5, 10)
        self.assertEqual(repr(d), "BulkDiscountPricing(threshold=5, percent_off=10)")

    def test_is_pricing_strategy(self) -> None:
        self.assertIsInstance(BulkDiscountPricing(FlatPricing(), 1, 1), PricingStrategy)


class BulkDiscountPriceTests(unittest.TestCase):
    def test_below_threshold_returns_base_total(self) -> None:
        items = [LineItem("EL-1001", 2, Money(1000))]
        d = BulkDiscountPricing(FlatPricing(), 3, 50)
        self.assertEqual(d.price(items), Money(2000))

    def test_at_threshold_applies_discount(self) -> None:
        items = [LineItem("EL-1001", 3, Money(1000))]
        d = BulkDiscountPricing(FlatPricing(), 3, 10)
        self.assertEqual(d.price(items), Money(2700))

    def test_quantity_summed_across_lines(self) -> None:
        items = [LineItem("EL-1001", 1, Money(1000)), LineItem("GR-2001", 2, Money(100))]
        d = BulkDiscountPricing(FlatPricing(), 3, 10)
        # base = 1000 + 200 = 1200; discount = 120 -> 1080
        self.assertEqual(d.price(items), Money(1080))

    def test_zero_percent_returns_base_even_above_threshold(self) -> None:
        items = [LineItem("EL-1001", 5, Money(100))]
        d = BulkDiscountPricing(FlatPricing(), 1, 0)
        self.assertEqual(d.price(items), Money(500))

    def test_discount_uses_floor_division(self) -> None:
        # base 333; 333 * 10 // 100 = 33 -> 300
        items = [LineItem("EL-1001", 1, Money(333))]
        d = BulkDiscountPricing(FlatPricing(), 1, 10)
        self.assertEqual(d.price(items), Money(300))

    def test_full_discount_yields_zero(self) -> None:
        items = [LineItem("EL-1001", 2, Money(500))]
        d = BulkDiscountPricing(FlatPricing(), 1, 100)
        self.assertEqual(d.price(items), Money(0))

    def test_wraps_base_with_tax(self) -> None:
        items = [LineItem("EL-1001", 1, Money(1000))]
        d = BulkDiscountPricing(FlatPricing(1000), 1, 10)
        # base with 10% tax = 1100; discount = 110 -> 990
        self.assertEqual(d.price(items), Money(990))

    def test_empty_items_below_threshold(self) -> None:
        d = BulkDiscountPricing(FlatPricing(), 1, 50)
        self.assertEqual(d.price([]), Money(0))

    def test_call_matches_price(self) -> None:
        items = [LineItem("EL-1001", 3, Money(100))]
        d = BulkDiscountPricing(FlatPricing(), 1, 10)
        self.assertEqual(d(items), d.price(items))


if __name__ == "__main__":
    unittest.main()
