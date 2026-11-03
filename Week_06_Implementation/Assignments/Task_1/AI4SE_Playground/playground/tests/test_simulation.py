"""Unit tests for the simulation module."""
from __future__ import annotations

import unittest
from typing import List, Mapping

from playground.base import PricingStrategy
from playground.enums import EventType, OrderStatus
from playground.events import EventBus
from playground.inventory import Warehouse
from playground.models import Customer, Money
from playground.orders import Order, OrderLog
from playground.pricing import FlatPricing
from playground.simulation import (
    Simulation,
    SimulationReport,
    build_default_warehouse,
    run_simulation,
)


class SimulationReportTests(unittest.TestCase):
    def test_defaults(self) -> None:
        r = SimulationReport()
        self.assertEqual(r.orders_created, 0)
        self.assertEqual(r.orders_shipped, 0)
        self.assertEqual(r.orders_cancelled, 0)
        self.assertEqual(r.rejected_out_of_stock, 0)
        self.assertEqual(r.revenue, Money(0))

    def test_record_created(self) -> None:
        r = SimulationReport()
        r.record("created")
        self.assertEqual(r.orders_created, 1)

    def test_record_shipped(self) -> None:
        r = SimulationReport()
        r.record("shipped")
        self.assertEqual(r.orders_shipped, 1)

    def test_record_cancelled(self) -> None:
        r = SimulationReport()
        r.record("cancelled")
        self.assertEqual(r.orders_cancelled, 1)

    def test_record_rejected(self) -> None:
        r = SimulationReport()
        r.record("rejected")
        r.record("rejected")
        self.assertEqual(r.rejected_out_of_stock, 2)

    def test_record_unknown_kind_rejected(self) -> None:
        r = SimulationReport()
        with self.assertRaises(ValueError):
            r.record("bogus")

    def test_record_is_case_sensitive(self) -> None:
        with self.assertRaises(ValueError):
            SimulationReport().record("Created")

    def test_add_revenue_accumulates(self) -> None:
        r = SimulationReport()
        r.add_revenue(Money(100))
        r.add_revenue(Money(250))
        self.assertEqual(r.revenue, Money(350))

    def test_add_revenue_non_money_rejected(self) -> None:
        with self.assertRaises(TypeError):
            SimulationReport().add_revenue(100)  # type: ignore[arg-type]

    def test_summary_contents(self) -> None:
        r = SimulationReport()
        r.record("created")
        r.record("shipped")
        r.record("cancelled")
        r.record("rejected")
        r.add_revenue(Money(1234))
        self.assertEqual(
            r.summary(),
            {
                "orders_created": 1,
                "orders_shipped": 1,
                "orders_cancelled": 1,
                "rejected_out_of_stock": 1,
                "revenue": "$12.34",
            },
        )

    def test_summary_zero_revenue_formatted(self) -> None:
        self.assertEqual(SimulationReport().summary()["revenue"], "$0.00")

    def test_str_is_multiline_summary(self) -> None:
        r = SimulationReport()
        r.record("created")
        text = str(r)
        lines = text.split("\n")
        self.assertEqual(len(lines), 5)
        self.assertIn("orders_created: 1", lines)
        self.assertIn("revenue: $0.00", lines)


class SimulationConstructionTests(unittest.TestCase):
    def test_warehouse_type_checked(self) -> None:
        with self.assertRaises(TypeError):
            Simulation(object(), FlatPricing())  # type: ignore[arg-type]

    def test_pricing_type_checked(self) -> None:
        with self.assertRaises(TypeError):
            Simulation(build_default_warehouse(), object())  # type: ignore[arg-type]

    def test_creates_default_bus_and_collaborators(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing())
        self.assertIsInstance(sim.bus, EventBus)
        self.assertIsInstance(sim.log, OrderLog)
        self.assertIsInstance(sim.report, SimulationReport)
        self.assertEqual(len(sim.log), 0)

    def test_uses_supplied_bus(self) -> None:
        bus = EventBus()
        sim = Simulation(build_default_warehouse(), FlatPricing(), bus=bus)
        self.assertIs(sim.bus, bus)

    def test_no_customers_step_returns_none(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing())
        self.assertIsNone(sim.step())
        self.assertEqual(sim.report.orders_created, 0)
        self.assertEqual(sim.report.rejected_out_of_stock, 0)

    def test_add_customer_non_customer_rejected(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing())
        with self.assertRaises(TypeError):
            sim.add_customer("alice")  # type: ignore[arg-type]


class SimulationStepTests(unittest.TestCase):
    def _sim(self, seed: int = 0, warehouse: Warehouse | None = None) -> Simulation:
        sim = Simulation(warehouse or build_default_warehouse(), FlatPricing(), seed=seed)
        sim.add_customer(Customer("C-1", "Alice", Money(10 ** 9)))
        return sim

    def test_no_stock_records_rejected_and_returns_none(self) -> None:
        wh = build_default_warehouse()
        for sku in list(wh.ledger):
            wh.ledger.reserve(sku, wh.ledger.available(sku)).commit()
        sim = self._sim(warehouse=wh)
        self.assertIsNone(sim.step())
        self.assertEqual(sim.report.rejected_out_of_stock, 1)

    def test_empty_ledger_no_skus_records_rejected(self) -> None:
        from playground.inventory import InventoryLedger
        from playground.repository import InMemoryRepository
        from playground.models import Product
        from playground.enums import Category

        repo = InMemoryRepository(Product)
        repo.add(Product("EL-1001", "X", Category.ELECTRONICS, Money(1)))
        wh = Warehouse("WH-2", "Empty", InventoryLedger(repo))
        sim = self._sim(warehouse=wh)
        self.assertIsNone(sim.step())
        self.assertEqual(sim.report.rejected_out_of_stock, 1)

    def test_step_returns_order_and_accounts_for_it(self) -> None:
        sim = self._sim(seed=1)
        order = sim.step()
        self.assertIsInstance(order, Order)
        self.assertIn(order.status, (OrderStatus.SHIPPED, OrderStatus.CANCELLED))
        self.assertEqual(len(sim.log), 1)
        self.assertEqual(sim.report.orders_created, 1)
        self.assertEqual(
            sim.report.orders_shipped + sim.report.orders_cancelled, 1
        )

    def test_order_ids_are_sequential(self) -> None:
        sim = self._sim(seed=2)
        first = sim.step()
        second = sim.step()
        self.assertEqual(first.order_id, "ORD-00001")
        self.assertEqual(second.order_id, "ORD-00002")

    def test_order_line_has_unit_price_1000_and_quantity_1_to_3(self) -> None:
        sim = self._sim(seed=3)
        order = sim.step()
        self.assertEqual(len(order), 1)
        line = order.items[0]
        self.assertIn(line.quantity, (1, 2, 3))
        self.assertEqual(line.unit_price, Money(1000))

    def test_shipped_path_publishes_and_adds_revenue(self) -> None:
        sim = self._sim(seed=0)
        seen: List[str] = []
        sim.bus.subscribe(EventType.ORDER_SHIPPED, lambda p: seen.append("shipped"))
        sim.bus.subscribe(EventType.STOCK_RESERVED, lambda p: seen.append("reserved"))
        sim.bus.subscribe(EventType.ORDER_CANCELLED, lambda p: seen.append("cancelled"))
        for _ in range(40):
            order = sim.step()
            if order is not None and order.status is OrderStatus.SHIPPED:
                break
        else:
            self.fail("no shipped order produced")
        self.assertIn("reserved", seen)
        self.assertIn("shipped", seen)
        self.assertNotIn("cancelled", seen[seen.index("reserved"):])
        self.assertGreater(sim.report.revenue.cents, 0)

    def test_cancel_path_releases_reservation(self) -> None:
        wh = build_default_warehouse()
        sim = self._sim(seed=0, warehouse=wh)
        cancelled_order = None
        for _ in range(200):
            on_hand_before = dict(wh.ledger._on_hand)  # type: ignore[attr-defined]
            order = sim.step()
            # No reservation may remain held after any step completes.
            self.assertTrue(all(v == 0 for v in wh.ledger._reserved.values()))  # type: ignore[attr-defined]
            if order is not None and order.status is OrderStatus.CANCELLED:
                cancelled_order = order
                # Cancelled orders must not reduce on-hand stock.
                self.assertEqual(wh.ledger._on_hand, on_hand_before)  # type: ignore[attr-defined]
                break
        self.assertIsNotNone(cancelled_order)
        self.assertGreaterEqual(sim.report.orders_cancelled, 1)

    def test_rejected_when_reserve_fails(self) -> None:
        wh = build_default_warehouse()
        sim = self._sim(seed=4, warehouse=wh)

        def always_out_of_stock(sku: str, quantity: int) -> None:
            from playground.exceptions import OutOfStockError

            raise OutOfStockError(sku, quantity, 0)

        wh.ledger.reserve = always_out_of_stock  # type: ignore[method-assign]
        self.assertIsNone(sim.step())
        self.assertEqual(sim.report.rejected_out_of_stock, 1)
        self.assertEqual(len(sim.log), 0)

    def test_reserved_event_payload_fields(self) -> None:
        sim = self._sim(seed=5)
        payloads: List[Mapping[str, object]] = []
        sim.bus.subscribe(EventType.STOCK_RESERVED, payloads.append)
        order = sim.step()
        self.assertEqual(len(payloads), 1)
        payload = payloads[0]
        self.assertEqual(payload["order_id"], order.order_id)
        self.assertEqual(payload["sku"], order.items[0].sku)
        self.assertEqual(payload["quantity"], order.items[0].quantity)

    def test_terminal_event_published_once_per_step(self) -> None:
        sim = self._sim(seed=6)
        terminal: List[str] = []
        sim.bus.subscribe(EventType.ORDER_SHIPPED, lambda p: terminal.append("S"))
        sim.bus.subscribe(EventType.ORDER_CANCELLED, lambda p: terminal.append("C"))
        for _ in range(5):
            sim.step()
        self.assertEqual(len(terminal), 5)

    def test_same_seed_is_reproducible(self) -> None:
        def run(seed: int) -> List[str]:
            sim = self._sim(seed=seed)
            return [sim.step().status.value for _ in range(15)]

        self.assertEqual(run(42), run(42))


class SimulationRunTests(unittest.TestCase):
    def test_run_zero_rejected(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing())
        with self.assertRaises(ValueError):
            sim.run(0)

    def test_run_non_int_rejected(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing())
        with self.assertRaises(TypeError):
            sim.run(2.5)  # type: ignore[arg-type]

    def test_run_returns_report(self) -> None:
        sim = Simulation(build_default_warehouse(), FlatPricing(), seed=1)
        sim.add_customer(Customer("C-1", "A", Money(10 ** 9)))
        report = sim.run(3)
        self.assertIs(report, sim.report)
        self.assertEqual(
            report.orders_shipped + report.orders_cancelled + report.rejected_out_of_stock,
            3,
        )


class BuildDefaultWarehouseTests(unittest.TestCase):
    def test_returns_warehouse_with_three_skus_each_20(self) -> None:
        wh = build_default_warehouse()
        self.assertIsInstance(wh, Warehouse)
        self.assertEqual(wh.identity(), "WH-1")
        self.assertEqual(
            wh.stock_report(), {"EL-1001": 20, "GR-2001": 20, "HW-3001": 20}
        )

    def test_products_have_expected_prices(self) -> None:
        wh = build_default_warehouse()
        repo = wh.ledger._product_repo  # type: ignore[attr-defined]
        self.assertEqual(repo.get("EL-1001").unit_price, Money(2500))
        self.assertEqual(repo.get("GR-2001").unit_price, Money(300))
        self.assertEqual(repo.get("HW-3001").unit_price, Money(1200))

    def test_each_call_returns_independent_warehouse(self) -> None:
        a = build_default_warehouse()
        b = build_default_warehouse()
        a.ledger.reserve("EL-1001", 1).commit()
        self.assertEqual(b.ledger.available("EL-1001"), 20)


class RunSimulationTests(unittest.TestCase):
    def test_bool_seed_rejected(self) -> None:
        with self.assertRaises(TypeError):
            run_simulation(True, 5)  # type: ignore[arg-type]

    def test_non_int_seed_rejected(self) -> None:
        with self.assertRaises(TypeError):
            run_simulation("1", 5)  # type: ignore[arg-type]

    def test_non_positive_steps_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_simulation(1, 0)

    def test_non_int_steps_rejected(self) -> None:
        with self.assertRaises(TypeError):
            run_simulation(1, "5")  # type: ignore[arg-type]

    def test_returns_report_with_totals(self) -> None:
        report = run_simulation(7, 25)
        self.assertIsInstance(report, SimulationReport)
        accounted = (
            report.orders_shipped + report.orders_cancelled + report.rejected_out_of_stock
        )
        self.assertEqual(accounted, 25)
        self.assertEqual(report.orders_created, report.orders_shipped + report.orders_cancelled)

    def test_deterministic_for_same_seed(self) -> None:
        self.assertEqual(run_simulation(11, 30).summary(), run_simulation(11, 30).summary())


if __name__ == "__main__":
    unittest.main()
