"""Unit tests for the playground package public API."""
from __future__ import annotations

import importlib
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

import playground


EXPECTED_EXPORTS = [
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


class PackageInitTests(unittest.TestCase):
    def test_version(self) -> None:
        self.assertEqual(playground.__version__, "0.1.0")

    def test_all_matches_expected_exports(self) -> None:
        self.assertEqual(sorted(playground.__all__), sorted(EXPECTED_EXPORTS))

    def test_every_export_resolves(self) -> None:
        for name in playground.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(playground, name))

    def test_reexports_are_the_defining_objects(self) -> None:
        from playground.models import Money
        from playground.exceptions import PlaygroundError
        from playground.simulation import run_simulation

        self.assertIs(playground.Money, Money)
        self.assertIs(playground.PlaygroundError, PlaygroundError)
        self.assertIs(playground.run_simulation, run_simulation)

    def test_import_has_no_output_side_effects(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            importlib.reload(playground)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_reload_keeps_version(self) -> None:
        reloaded = importlib.reload(playground)
        self.assertEqual(reloaded.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
