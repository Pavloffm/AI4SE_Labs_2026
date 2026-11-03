"""Unit tests for the enums module."""
from __future__ import annotations

import unittest

from playground.enums import Category, EventType, OrderStatus


class CategoryTests(unittest.TestCase):
    def test_member_values(self) -> None:
        self.assertEqual(Category.ELECTRONICS.value, "electronics")
        self.assertEqual(Category.GROCERY.value, "grocery")
        self.assertEqual(Category.APPAREL.value, "apparel")
        self.assertEqual(Category.HARDWARE.value, "hardware")

    def test_from_label_exact_match(self) -> None:
        self.assertIs(Category.from_label("grocery"), Category.GROCERY)

    def test_from_label_strips_and_lowercases(self) -> None:
        self.assertIs(Category.from_label("  HARDWARE  "), Category.HARDWARE)
        self.assertIs(Category.from_label("Apparel"), Category.APPAREL)

    def test_from_label_resolves_every_member(self) -> None:
        for member in Category:
            with self.subTest(member=member):
                self.assertIs(Category.from_label(member.value), member)

    def test_from_label_non_str_raises_type_error(self) -> None:
        for bad in (None, 1, b"grocery", Category.GROCERY):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    Category.from_label(bad)  # type: ignore[arg-type]

    def test_from_label_unknown_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Category.from_label(" Toys ")
        self.assertIn("unknown category", str(ctx.exception))
        self.assertIn("' Toys '", str(ctx.exception))

    def test_from_label_empty_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            Category.from_label("")

    def test_str_returns_value(self) -> None:
        for member in Category:
            with self.subTest(member=member):
                self.assertEqual(str(member), member.value)


class OrderStatusTests(unittest.TestCase):
    def test_member_values(self) -> None:
        self.assertEqual(OrderStatus.NEW.value, "new")
        self.assertEqual(OrderStatus.RESERVED.value, "reserved")
        self.assertEqual(OrderStatus.SHIPPED.value, "shipped")
        self.assertEqual(OrderStatus.CANCELLED.value, "cancelled")

    def test_shipped_is_terminal(self) -> None:
        self.assertIs(OrderStatus.SHIPPED.is_terminal, True)

    def test_cancelled_is_terminal(self) -> None:
        self.assertIs(OrderStatus.CANCELLED.is_terminal, True)

    def test_new_is_not_terminal(self) -> None:
        self.assertIs(OrderStatus.NEW.is_terminal, False)

    def test_reserved_is_not_terminal(self) -> None:
        self.assertIs(OrderStatus.RESERVED.is_terminal, False)


class EventTypeTests(unittest.TestCase):
    def test_values(self) -> None:
        self.assertEqual(EventType.STOCK_ADDED.value, 1)
        self.assertEqual(EventType.STOCK_RESERVED.value, 2)
        self.assertEqual(EventType.STOCK_RELEASED.value, 3)
        self.assertEqual(EventType.ORDER_SHIPPED.value, 4)
        self.assertEqual(EventType.ORDER_CANCELLED.value, 5)

    def test_members_are_hashable_and_distinct(self) -> None:
        self.assertEqual(len({member for member in EventType}), 5)


if __name__ == "__main__":
    unittest.main()
