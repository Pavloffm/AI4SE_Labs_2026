"""Unit tests for the exceptions module."""
from __future__ import annotations

import unittest

from playground import exceptions as exc_mod
from playground.exceptions import (
    DuplicateEntityError,
    InvalidTransitionError,
    InventoryError,
    OutOfStockError,
    PlaygroundError,
    UnknownSKUError,
)


class ExceptionHierarchyTests(unittest.TestCase):
    def test_root_derives_from_exception(self) -> None:
        self.assertTrue(issubclass(PlaygroundError, Exception))

    def test_inventory_error_derives_from_root(self) -> None:
        self.assertTrue(issubclass(InventoryError, PlaygroundError))

    def test_out_of_stock_derives_from_inventory_error(self) -> None:
        self.assertTrue(issubclass(OutOfStockError, InventoryError))
        self.assertTrue(issubclass(OutOfStockError, PlaygroundError))

    def test_unknown_sku_derives_from_inventory_error(self) -> None:
        self.assertTrue(issubclass(UnknownSKUError, InventoryError))
        self.assertTrue(issubclass(UnknownSKUError, PlaygroundError))

    def test_duplicate_entity_derives_from_root_only(self) -> None:
        self.assertTrue(issubclass(DuplicateEntityError, PlaygroundError))
        self.assertFalse(issubclass(DuplicateEntityError, InventoryError))

    def test_invalid_transition_derives_from_root_only(self) -> None:
        self.assertTrue(issubclass(InvalidTransitionError, PlaygroundError))
        self.assertFalse(issubclass(InvalidTransitionError, InventoryError))

    def test_every_class_is_playground_error_subclass(self) -> None:
        names = [
            "PlaygroundError",
            "InventoryError",
            "OutOfStockError",
            "UnknownSKUError",
            "DuplicateEntityError",
            "InvalidTransitionError",
        ]
        self.assertEqual(len(names), 6)
        for name in names:
            with self.subTest(name=name):
                cls = getattr(exc_mod, name)
                self.assertTrue(issubclass(cls, PlaygroundError))

    def test_root_catches_all_subclasses(self) -> None:
        for exc in (
            InventoryError("x"),
            OutOfStockError("A-1", 1, 0),
            UnknownSKUError("A-1"),
            DuplicateEntityError("k"),
            InvalidTransitionError("a", "b"),
        ):
            with self.subTest(exc=type(exc).__name__):
                with self.assertRaises(PlaygroundError):
                    raise exc


class OutOfStockErrorTests(unittest.TestCase):
    def test_attributes_are_set(self) -> None:
        err = OutOfStockError("EL-1001", 6, 5)
        self.assertEqual(err.sku, "EL-1001")
        self.assertEqual(err.requested, 6)
        self.assertEqual(err.available, 5)

    def test_message_format(self) -> None:
        err = OutOfStockError("EL-1001", 6, 5)
        self.assertEqual(
            str(err), "insufficient stock for EL-1001: requested 6, available 5"
        )

    def test_is_catchable_as_inventory_error(self) -> None:
        with self.assertRaises(InventoryError):
            raise OutOfStockError("EL-1001", 1, 0)


class UnknownSKUErrorTests(unittest.TestCase):
    def test_attribute_and_message(self) -> None:
        err = UnknownSKUError("ZZ-9999")
        self.assertEqual(err.sku, "ZZ-9999")
        self.assertEqual(str(err), "unknown SKU: ZZ-9999")


class DuplicateEntityErrorTests(unittest.TestCase):
    def test_attribute_and_message(self) -> None:
        err = DuplicateEntityError("C-1")
        self.assertEqual(err.key, "C-1")
        self.assertEqual(str(err), "duplicate entity: C-1")


class InvalidTransitionErrorTests(unittest.TestCase):
    def test_attributes_and_message(self) -> None:
        err = InvalidTransitionError("new", "shipped")
        self.assertEqual(err.source, "new")
        self.assertEqual(err.target, "shipped")
        self.assertEqual(str(err), "invalid transition: 'new' -> 'shipped'")

    def test_accepts_arbitrary_objects(self) -> None:
        err = InvalidTransitionError(3, 7)
        self.assertEqual(err.source, 3)
        self.assertEqual(err.target, 7)


if __name__ == "__main__":
    unittest.main()
