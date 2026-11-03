"""Unit tests for the inventory module."""
from __future__ import annotations

import unittest

from playground.base import Repository
from playground.enums import Category
from playground.exceptions import (
    InvalidTransitionError,
    InventoryError,
    OutOfStockError,
    UnknownSKUError,
)
from playground.inventory import InventoryLedger, ReservationContext, Warehouse
from playground.models import Money, Product
from playground.repository import InMemoryRepository


def _make_repo() -> InMemoryRepository:
    repo = InMemoryRepository(Product)
    repo.add(Product("EL-1001", "Headphones", Category.ELECTRONICS, Money(2500)))
    repo.add(Product("GR-2001", "Beans", Category.GROCERY, Money(300)))
    return repo


class InventoryLedgerConstructionTests(unittest.TestCase):
    def test_requires_repository(self) -> None:
        with self.assertRaises(TypeError):
            InventoryLedger({})  # type: ignore[arg-type]

    def test_accepts_repository(self) -> None:
        ledger = InventoryLedger(_make_repo())
        self.assertEqual(len(ledger), 0)


class InventoryLedgerStockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())

    def test_add_stock_returns_new_on_hand(self) -> None:
        self.assertEqual(self.ledger.add_stock("EL-1001", 5), 5)
        self.assertEqual(self.ledger.add_stock("EL-1001", 3), 8)

    def test_add_stock_normalizes_sku(self) -> None:
        self.assertEqual(self.ledger.add_stock(" el-1001 ", 2), 2)
        self.assertEqual(self.ledger.available("EL-1001"), 2)

    def test_add_stock_unknown_sku(self) -> None:
        with self.assertRaises(UnknownSKUError) as ctx:
            self.ledger.add_stock("ZZ-9999", 1)
        self.assertEqual(ctx.exception.sku, "ZZ-9999")

    def test_add_stock_invalid_sku_chars(self) -> None:
        with self.assertRaises(ValueError):
            self.ledger.add_stock("EL_1001", 1)

    def test_add_stock_invalid_quantity_bool(self) -> None:
        with self.assertRaises(TypeError):
            self.ledger.add_stock("EL-1001", True)  # type: ignore[arg-type]

    def test_add_stock_zero_quantity(self) -> None:
        with self.assertRaises(ValueError):
            self.ledger.add_stock("EL-1001", 0)

    def test_quantity_validated_before_sku(self) -> None:
        # Bad quantity on an unknown SKU must raise the quantity error first.
        with self.assertRaises(ValueError):
            self.ledger.add_stock("ZZ-9999", 0)

    def test_available_defaults_to_zero_when_no_stock(self) -> None:
        self.assertEqual(self.ledger.available("EL-1001"), 0)

    def test_available_unknown_sku(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.ledger.available("ZZ-9999")

    def test_available_normalizes(self) -> None:
        self.ledger.add_stock("GR-2001", 4)
        self.assertEqual(self.ledger.available("gr-2001"), 4)

    def test_require_sku_returns_normalized(self) -> None:
        self.assertEqual(self.ledger._require_sku(" gr-2001 "), "GR-2001")

    def test_require_sku_unknown_raises(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.ledger._require_sku("GR-9999")

    def test_require_sku_malformed_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.ledger._require_sku("x")


class InventoryLedgerReserveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())
        self.ledger.add_stock("EL-1001", 10)

    def test_reserve_returns_context_and_reduces_available(self) -> None:
        ctx = self.ledger.reserve("EL-1001", 4)
        self.assertIsInstance(ctx, ReservationContext)
        self.assertEqual(ctx.state, "held")
        self.assertEqual(self.ledger.available("EL-1001"), 6)

    def test_reserve_exact_available_allowed(self) -> None:
        self.ledger.reserve("EL-1001", 10)
        self.assertEqual(self.ledger.available("EL-1001"), 0)

    def test_reserve_over_available_raises_out_of_stock(self) -> None:
        with self.assertRaises(OutOfStockError) as ctx:
            self.ledger.reserve("EL-1001", 11)
        self.assertEqual(ctx.exception.sku, "EL-1001")
        self.assertEqual(ctx.exception.requested, 11)
        self.assertEqual(ctx.exception.available, 10)
        self.assertEqual(self.ledger.available("EL-1001"), 10)

    def test_reserve_considers_existing_reservations(self) -> None:
        self.ledger.reserve("EL-1001", 8)
        with self.assertRaises(OutOfStockError) as ctx:
            self.ledger.reserve("EL-1001", 3)
        self.assertEqual(ctx.exception.available, 2)

    def test_reserve_unknown_sku(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.ledger.reserve("ZZ-9999", 1)

    def test_reserve_bad_quantity(self) -> None:
        with self.assertRaises(TypeError):
            self.ledger.reserve("EL-1001", 1.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.ledger.reserve("EL-1001", -1)

    def test_reserve_out_of_stock_on_unstocked_sku(self) -> None:
        with self.assertRaises(OutOfStockError) as ctx:
            self.ledger.reserve("GR-2001", 1)
        self.assertEqual(ctx.exception.available, 0)


class InventoryLedgerReleaseCommitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())
        self.ledger.add_stock("EL-1001", 10)

    def test_release_restores_available(self) -> None:
        self.ledger.reserve("EL-1001", 4)
        self.ledger.release("EL-1001", 4)
        self.assertEqual(self.ledger.available("EL-1001"), 10)

    def test_release_partial(self) -> None:
        self.ledger.reserve("EL-1001", 4)
        self.ledger.release("EL-1001", 1)
        self.assertEqual(self.ledger.available("EL-1001"), 7)

    def test_release_more_than_reserved_raises(self) -> None:
        self.ledger.reserve("EL-1001", 2)
        with self.assertRaises(InvalidTransitionError) as ctx:
            self.ledger.release("EL-1001", 3)
        self.assertEqual(ctx.exception.source, 2)
        self.assertEqual(ctx.exception.target, 3)
        self.assertEqual(self.ledger.available("EL-1001"), 8)

    def test_release_with_nothing_reserved_raises(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            self.ledger.release("EL-1001", 1)

    def test_release_unknown_sku(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.ledger.release("ZZ-9999", 1)

    def test_release_bad_quantity(self) -> None:
        with self.assertRaises(ValueError):
            self.ledger.release("EL-1001", 0)

    def test_commit_reduces_on_hand_and_reserved(self) -> None:
        self.ledger.reserve("EL-1001", 3)
        self.ledger.commit("EL-1001", 3)
        self.assertEqual(self.ledger.available("EL-1001"), 7)
        self.assertEqual(self.ledger._on_hand["EL-1001"], 7)
        self.assertEqual(self.ledger._reserved["EL-1001"], 0)

    def test_commit_partial_keeps_remaining_hold(self) -> None:
        self.ledger.reserve("EL-1001", 5)
        self.ledger.commit("EL-1001", 2)
        self.assertEqual(self.ledger._on_hand["EL-1001"], 8)
        self.assertEqual(self.ledger._reserved["EL-1001"], 3)
        self.assertEqual(self.ledger.available("EL-1001"), 5)

    def test_commit_more_than_reserved_raises(self) -> None:
        self.ledger.reserve("EL-1001", 1)
        with self.assertRaises(InvalidTransitionError) as ctx:
            self.ledger.commit("EL-1001", 2)
        self.assertEqual(ctx.exception.source, 1)
        self.assertEqual(ctx.exception.target, 2)
        self.assertEqual(self.ledger._on_hand["EL-1001"], 10)

    def test_commit_with_nothing_reserved_raises(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            self.ledger.commit("EL-1001", 1)

    def test_commit_unknown_sku(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.ledger.commit("ZZ-9999", 1)

    def test_commit_bad_quantity(self) -> None:
        with self.assertRaises(TypeError):
            self.ledger.commit("EL-1001", "1")  # type: ignore[arg-type]


class InventoryLedgerContainsLenIterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())

    def test_contains_non_str_false(self) -> None:
        self.ledger.add_stock("EL-1001", 1)
        self.assertFalse(5 in self.ledger)  # type: ignore[operator]

    def test_contains_malformed_string_false(self) -> None:
        self.assertFalse("x" in self.ledger)
        self.assertFalse("EL_1001" in self.ledger)

    def test_contains_normalized_present(self) -> None:
        self.ledger.add_stock("EL-1001", 1)
        self.assertTrue(" el-1001 " in self.ledger)

    def test_contains_valid_but_unstocked_false(self) -> None:
        self.assertFalse("EL-1001" in self.ledger)

    def test_contains_false_if_zero_on_hand_after_commit(self) -> None:
        # A retained _on_hand key is not contained once its quantity reaches zero.
        self.ledger.add_stock("EL-1001", 2)
        self.ledger.reserve("EL-1001", 2)
        self.ledger.commit("EL-1001", 2)
        self.assertFalse("EL-1001" in self.ledger)

    def test_len_counts_positive_on_hand_only(self) -> None:
        self.assertEqual(len(self.ledger), 0)
        self.ledger.add_stock("EL-1001", 1)
        self.ledger.add_stock("GR-2001", 1)
        self.assertEqual(len(self.ledger), 2)

    def test_len_excludes_fully_committed_sku(self) -> None:
        self.ledger.add_stock("EL-1001", 2)
        self.ledger.add_stock("GR-2001", 1)
        self.ledger.reserve("EL-1001", 2)
        self.ledger.commit("EL-1001", 2)
        self.assertEqual(len(self.ledger), 1)

    def test_iter_sorted_and_positive_only(self) -> None:
        self.ledger.add_stock("GR-2001", 1)
        self.ledger.add_stock("EL-1001", 1)
        self.assertEqual(list(self.ledger), ["EL-1001", "GR-2001"])

    def test_iter_skips_zeroed_skus(self) -> None:
        self.ledger.add_stock("EL-1001", 2)
        self.ledger.add_stock("GR-2001", 1)
        self.ledger.reserve("EL-1001", 2)
        self.ledger.commit("EL-1001", 2)
        self.assertEqual(list(self.ledger), ["GR-2001"])

    def test_iter_empty(self) -> None:
        self.assertEqual(list(self.ledger), [])


class ReservationContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())
        self.ledger.add_stock("EL-1001", 10)

    def test_initial_state_held(self) -> None:
        rc = ReservationContext(self.ledger, "EL-1001", 1)
        self.assertEqual(rc.state, "held")

    def test_enter_returns_self(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        with rc as entered:
            self.assertIs(entered, rc)

    def test_exit_without_commit_releases(self) -> None:
        with self.ledger.reserve("EL-1001", 3) as rc:
            self.assertEqual(self.ledger.available("EL-1001"), 7)
        self.assertEqual(rc.state, "released")
        self.assertEqual(self.ledger.available("EL-1001"), 10)

    def test_commit_inside_block_keeps_stock_consumed(self) -> None:
        with self.ledger.reserve("EL-1001", 3) as rc:
            rc.commit()
            self.assertEqual(rc.state, "committed")
        self.assertEqual(rc.state, "committed")
        self.assertEqual(self.ledger.available("EL-1001"), 7)
        self.assertEqual(self.ledger._on_hand["EL-1001"], 7)

    def test_exception_inside_block_releases_and_propagates(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        with self.assertRaises(RuntimeError):
            with rc:
                raise RuntimeError("boom")
        self.assertEqual(rc.state, "released")
        self.assertEqual(self.ledger.available("EL-1001"), 10)

    def test_exit_returns_false(self) -> None:
        rc = self.ledger.reserve("EL-1001", 1)
        self.assertIs(rc.__exit__(None, None, None), False)
        self.assertEqual(rc.state, "released")

    def test_exit_when_already_committed_does_not_release(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        rc.commit()
        before = self.ledger.available("EL-1001")
        self.assertIs(rc.__exit__(None, None, None), False)
        self.assertEqual(self.ledger.available("EL-1001"), before)
        self.assertEqual(rc.state, "committed")

    def test_exit_when_already_released_is_noop(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        rc.__exit__(None, None, None)
        before = self.ledger.available("EL-1001")
        rc.__exit__(None, None, None)
        self.assertEqual(self.ledger.available("EL-1001"), before)

    def test_enter_after_release_raises(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        with rc:
            pass
        with self.assertRaises(InvalidTransitionError) as ctx:
            rc.__enter__()
        self.assertEqual(ctx.exception.source, "released")
        self.assertEqual(ctx.exception.target, "held")

    def test_enter_after_commit_raises(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        rc.commit()
        with self.assertRaises(InvalidTransitionError):
            with rc:
                pass

    def test_commit_twice_raises(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        rc.commit()
        with self.assertRaises(InvalidTransitionError) as ctx:
            rc.commit()
        self.assertEqual(ctx.exception.source, "committed")
        self.assertEqual(ctx.exception.target, "committed")

    def test_commit_after_release_raises(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        with rc:
            pass
        with self.assertRaises(InvalidTransitionError):
            rc.commit()

    def test_repr(self) -> None:
        rc = self.ledger.reserve("EL-1001", 2)
        self.assertEqual(repr(rc), "ReservationContext('EL-1001', 2, 'held')")
        rc.commit()
        self.assertEqual(repr(rc), "ReservationContext('EL-1001', 2, 'committed')")


class WarehouseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = InventoryLedger(_make_repo())
        self.wh = Warehouse("WH-1", "Main", self.ledger)

    def test_identity(self) -> None:
        self.assertEqual(self.wh.identity(), "WH-1")

    def test_ledger_property(self) -> None:
        self.assertIs(self.wh.ledger, self.ledger)

    def test_empty_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Warehouse("  ", "Main", self.ledger)

    def test_non_str_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Warehouse(None, "Main", self.ledger)  # type: ignore[arg-type]

    def test_non_ledger_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Warehouse("WH-1", "Main", object())  # type: ignore[arg-type]

    def test_receive_delegates_and_returns_on_hand(self) -> None:
        self.assertEqual(self.wh.receive("EL-1001", 4), 4)
        self.assertEqual(self.wh.receive("EL-1001", 1), 5)
        self.assertEqual(self.ledger.available("EL-1001"), 5)

    def test_receive_unknown_sku_propagates(self) -> None:
        with self.assertRaises(UnknownSKUError):
            self.wh.receive("ZZ-9999", 1)

    def test_receive_bad_quantity_propagates(self) -> None:
        with self.assertRaises(ValueError):
            self.wh.receive("EL-1001", 0)

    def test_stock_report_lists_available(self) -> None:
        self.wh.receive("GR-2001", 3)
        self.wh.receive("EL-1001", 2)
        self.ledger.reserve("EL-1001", 1)
        self.assertEqual(self.wh.stock_report(), {"EL-1001": 1, "GR-2001": 3})

    def test_stock_report_empty(self) -> None:
        self.assertEqual(self.wh.stock_report(), {})

    def test_repr(self) -> None:
        self.assertEqual(repr(self.wh), "Warehouse('WH-1', 'Main')")

    def test_equality_by_id(self) -> None:
        other = Warehouse("WH-1", "Other", InventoryLedger(_make_repo()))
        self.assertEqual(self.wh, other)


class InventoryErrorHierarchyTests(unittest.TestCase):
    def test_out_of_stock_is_inventory_error(self) -> None:
        ledger = InventoryLedger(_make_repo())
        with self.assertRaises(InventoryError):
            ledger.reserve("EL-1001", 1)


if __name__ == "__main__":
    unittest.main()
