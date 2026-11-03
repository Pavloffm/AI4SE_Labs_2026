"""Unit tests for the orders module."""
from __future__ import annotations

import unittest

from playground.base import PricingStrategy
from playground.enums import OrderStatus
from playground.exceptions import DuplicateEntityError, InvalidTransitionError
from playground.models import Customer, LineItem, Money
from playground.orders import Order, OrderBuilder, OrderLog, OrderStateMachine
from playground.pricing import BulkDiscountPricing, FlatPricing


def _customer() -> Customer:
    return Customer("C-1", "Alice", Money(1000000))


def _order(order_id: str = "ORD-1", pricing: PricingStrategy | None = None) -> Order:
    return Order(order_id, _customer(), pricing or FlatPricing())


class OrderStateMachineTests(unittest.TestCase):
    def test_new_can_reach_reserved_and_cancelled(self) -> None:
        sm = OrderStateMachine()
        self.assertTrue(sm.can_transition(OrderStatus.NEW, OrderStatus.RESERVED))
        self.assertTrue(sm.can_transition(OrderStatus.NEW, OrderStatus.CANCELLED))

    def test_new_cannot_ship_directly(self) -> None:
        self.assertFalse(OrderStateMachine().can_transition(OrderStatus.NEW, OrderStatus.SHIPPED))

    def test_reserved_can_ship_or_cancel(self) -> None:
        sm = OrderStateMachine()
        self.assertTrue(sm.can_transition(OrderStatus.RESERVED, OrderStatus.SHIPPED))
        self.assertTrue(sm.can_transition(OrderStatus.RESERVED, OrderStatus.CANCELLED))

    def test_reserved_cannot_return_to_new(self) -> None:
        self.assertFalse(OrderStateMachine().can_transition(OrderStatus.RESERVED, OrderStatus.NEW))

    def test_terminal_states_have_no_outgoing(self) -> None:
        sm = OrderStateMachine()
        for source in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            for target in OrderStatus:
                with self.subTest(source=source, target=target):
                    self.assertFalse(sm.can_transition(source, target))

    def test_allowed_from_returns_frozenset(self) -> None:
        allowed = OrderStateMachine.allowed_from(OrderStatus.NEW)
        self.assertIsInstance(allowed, frozenset)
        self.assertEqual(allowed, frozenset({OrderStatus.RESERVED, OrderStatus.CANCELLED}))

    def test_allowed_from_terminal_is_empty(self) -> None:
        self.assertEqual(OrderStateMachine.allowed_from(OrderStatus.SHIPPED), frozenset())

    def test_allowed_from_non_status_raises(self) -> None:
        with self.assertRaises(TypeError):
            OrderStateMachine.allowed_from("new")  # type: ignore[arg-type]

    def test_transition_returns_target_when_legal(self) -> None:
        sm = OrderStateMachine()
        self.assertIs(sm.transition(OrderStatus.NEW, OrderStatus.RESERVED), OrderStatus.RESERVED)

    def test_transition_illegal_raises(self) -> None:
        with self.assertRaises(InvalidTransitionError) as ctx:
            OrderStateMachine().transition(OrderStatus.NEW, OrderStatus.SHIPPED)
        self.assertIs(ctx.exception.source, OrderStatus.NEW)
        self.assertIs(ctx.exception.target, OrderStatus.SHIPPED)

    def test_call_is_alias_for_transition(self) -> None:
        sm = OrderStateMachine()
        self.assertIs(sm(OrderStatus.RESERVED, OrderStatus.SHIPPED), OrderStatus.SHIPPED)
        with self.assertRaises(InvalidTransitionError):
            sm(OrderStatus.SHIPPED, OrderStatus.NEW)


class OrderConstructionTests(unittest.TestCase):
    def test_initial_state(self) -> None:
        o = _order("ORD-9")
        self.assertEqual(o.order_id, "ORD-9")
        self.assertEqual(o.customer.customer_id, "C-1")
        self.assertIs(o.status, OrderStatus.NEW)
        self.assertEqual(o.items, ())
        self.assertEqual(len(o), 0)

    def test_empty_order_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Order("  ", _customer(), FlatPricing())

    def test_non_str_order_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Order(None, _customer(), FlatPricing())  # type: ignore[arg-type]

    def test_non_customer_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Order("ORD-1", "alice", FlatPricing())  # type: ignore[arg-type]

    def test_non_pricing_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Order("ORD-1", _customer(), lambda items: Money(0))  # type: ignore[arg-type]

    def test_customer_property(self) -> None:
        c = _customer()
        o = Order("ORD-1", c, FlatPricing())
        self.assertIs(o.customer, c)


class OrderAddItemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.order = _order()

    def test_add_appends_new_sku(self) -> None:
        self.order.add_item(LineItem("EL-1001", 1, Money(250)))
        self.order.add_item(LineItem("GR-2001", 2, Money(100)))
        self.assertEqual(len(self.order), 2)
        self.assertEqual([i.sku for i in self.order.items], ["EL-1001", "GR-2001"])

    def test_add_same_sku_merges_quantity(self) -> None:
        self.order.add_item(LineItem("EL-1001", 1, Money(250)))
        self.order.add_item(LineItem("EL-1001", 2, Money(250)))
        self.assertEqual(len(self.order), 1)
        self.assertEqual(self.order.items[0].quantity, 3)

    def test_merge_keeps_position(self) -> None:
        self.order.add_item(LineItem("AA-1", 1, Money(1)))
        self.order.add_item(LineItem("BB-1", 1, Money(1)))
        self.order.add_item(LineItem("AA-1", 4, Money(1)))
        self.assertEqual([i.sku for i in self.order.items], ["AA-1", "BB-1"])
        self.assertEqual(self.order.items[0].quantity, 5)

    def test_non_line_item_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.order.add_item(("EL-1001", 1, Money(1)))  # type: ignore[arg-type]

    def test_add_after_advance_rejected(self) -> None:
        self.order.add_item(LineItem("EL-1001", 1, Money(1)))
        self.order.advance(OrderStatus.RESERVED)
        with self.assertRaises(InvalidTransitionError) as ctx:
            self.order.add_item(LineItem("GR-2001", 1, Money(1)))
        self.assertIs(ctx.exception.source, OrderStatus.RESERVED)
        self.assertIs(ctx.exception.target, OrderStatus.NEW)

    def test_add_after_cancel_rejected(self) -> None:
        self.order.advance(OrderStatus.CANCELLED)
        with self.assertRaises(InvalidTransitionError):
            self.order.add_item(LineItem("GR-2001", 1, Money(1)))


class OrderAdvanceTests(unittest.TestCase):
    def test_happy_path_to_shipped(self) -> None:
        o = _order()
        o.advance(OrderStatus.RESERVED)
        self.assertIs(o.status, OrderStatus.RESERVED)
        o.advance(OrderStatus.SHIPPED)
        self.assertIs(o.status, OrderStatus.SHIPPED)

    def test_cancel_from_new(self) -> None:
        o = _order()
        o.advance(OrderStatus.CANCELLED)
        self.assertIs(o.status, OrderStatus.CANCELLED)

    def test_cancel_from_reserved(self) -> None:
        o = _order()
        o.advance(OrderStatus.RESERVED)
        o.advance(OrderStatus.CANCELLED)
        self.assertIs(o.status, OrderStatus.CANCELLED)

    def test_illegal_advance_raises_and_keeps_status(self) -> None:
        o = _order()
        with self.assertRaises(InvalidTransitionError):
            o.advance(OrderStatus.SHIPPED)
        self.assertIs(o.status, OrderStatus.NEW)

    def test_advance_from_terminal_raises(self) -> None:
        o = _order()
        o.advance(OrderStatus.CANCELLED)
        with self.assertRaises(InvalidTransitionError):
            o.advance(OrderStatus.RESERVED)

    def test_advance_to_same_status_raises(self) -> None:
        o = _order()
        with self.assertRaises(InvalidTransitionError):
            o.advance(OrderStatus.NEW)


class OrderTotalTests(unittest.TestCase):
    def test_total_empty_is_zero(self) -> None:
        self.assertEqual(_order().total, Money(0))

    def test_total_uses_pricing_strategy(self) -> None:
        o = _order(pricing=FlatPricing(800))
        o.add_item(LineItem("EL-1001", 1, Money(1000)))
        self.assertEqual(o.total, Money(1080))

    def test_total_reflects_merged_quantities_for_bulk_discount(self) -> None:
        o = _order(pricing=BulkDiscountPricing(FlatPricing(), 3, 10))
        o.add_item(LineItem("EL-1001", 1, Money(100)))
        o.add_item(LineItem("EL-1001", 2, Money(100)))
        # 3 units at 100 = 300, 10% off = 270
        self.assertEqual(o.total, Money(270))


class OrderContainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.order = _order()
        self.order.add_item(LineItem("EL-1001", 1, Money(1)))
        self.order.add_item(LineItem("GR-2001", 2, Money(1)))

    def test_items_is_tuple_copy(self) -> None:
        items = self.order.items
        self.assertIsInstance(items, tuple)
        self.order.add_item(LineItem("HW-3001", 1, Money(1)))
        self.assertEqual(len(items), 2)
        self.assertEqual(len(self.order.items), 3)

    def test_len(self) -> None:
        self.assertEqual(len(self.order), 2)

    def test_iter_yields_line_items(self) -> None:
        self.assertEqual([i.sku for i in self.order], ["EL-1001", "GR-2001"])

    def test_iter_is_snapshot(self) -> None:
        it = iter(self.order)
        self.order.add_item(LineItem("HW-3001", 1, Money(1)))
        self.assertEqual(len(list(it)), 2)


class OrderEqualityTests(unittest.TestCase):
    def test_equal_by_order_id(self) -> None:
        self.assertEqual(_order("ORD-1"), _order("ORD-1"))

    def test_not_equal_different_id(self) -> None:
        self.assertNotEqual(_order("ORD-1"), _order("ORD-2"))

    def test_eq_non_order_returns_not_implemented(self) -> None:
        self.assertIs(_order().__eq__("ORD-1"), NotImplemented)
        self.assertFalse(_order("ORD-1") == "ORD-1")

    def test_hash_by_id(self) -> None:
        self.assertEqual(hash(_order("ORD-1")), hash(("Order", "ORD-1")))
        self.assertEqual(len({_order("ORD-1"), _order("ORD-1")}), 1)

    def test_repr_includes_status(self) -> None:
        o = _order("ORD-7")
        self.assertEqual(repr(o), "Order('ORD-7', new)")
        o.advance(OrderStatus.CANCELLED)
        self.assertEqual(repr(o), "Order('ORD-7', cancelled)")


class OrderBuilderTests(unittest.TestCase):
    def test_constructor_type_checks(self) -> None:
        with self.assertRaises(TypeError):
            OrderBuilder("alice", FlatPricing())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            OrderBuilder(_customer(), object())  # type: ignore[arg-type]

    def test_for_customer_uses_flat_pricing(self) -> None:
        builder = OrderBuilder.for_customer(_customer())
        builder.add("EL-1001", 1, Money(1000))
        order = builder.build("ORD-1")
        self.assertIsInstance(order._pricing, FlatPricing)
        self.assertEqual(order.total, Money(1000))

    def test_for_customer_is_classmethod_returning_subclass(self) -> None:
        class _Sub(OrderBuilder):
            pass

        self.assertIsInstance(_Sub.for_customer(_customer()), _Sub)

    def test_add_returns_self_for_chaining(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        self.assertIs(b.add("EL-1001", 1, Money(1)), b)

    def test_add_validates_via_line_item(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        with self.assertRaises(ValueError):
            b.add("x", 1, Money(1))
        with self.assertRaises(ValueError):
            b.add("EL-1001", 0, Money(1))
        with self.assertRaises(TypeError):
            b.add("EL-1001", 1, 5)  # type: ignore[arg-type]
        self.assertEqual(len(b), 0)

    def test_add_normalizes_sku(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        b.add(" el-1001 ", 1, Money(1))
        order = b.build("ORD-1")
        self.assertEqual(order.items[0].sku, "EL-1001")

    def test_build_empty_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            OrderBuilder(_customer(), FlatPricing()).build("ORD-1")
        self.assertEqual(str(ctx.exception), "no items")

    def test_build_produces_order_with_lines(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing(0))
        b.add("EL-1001", 2, Money(250)).add("GR-2001", 1, Money(300))
        order = b.build("ORD-5")
        self.assertIsInstance(order, Order)
        self.assertEqual(order.order_id, "ORD-5")
        self.assertIs(order.status, OrderStatus.NEW)
        self.assertEqual(order.total, Money(800))

    def test_build_merges_duplicate_skus(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        b.add("EL-1001", 1, Money(100)).add("EL-1001", 2, Money(100))
        order = b.build("ORD-1")
        self.assertEqual(len(order), 1)
        self.assertEqual(order.items[0].quantity, 3)

    def test_build_twice_creates_independent_orders(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        b.add("EL-1001", 1, Money(1))
        o1 = b.build("ORD-1")
        b.add("GR-2001", 1, Money(1))
        o2 = b.build("ORD-2")
        self.assertEqual(len(o1), 1)
        self.assertEqual(len(o2), 2)

    def test_build_propagates_bad_order_id(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        b.add("EL-1001", 1, Money(1))
        with self.assertRaises(ValueError):
            b.build("")

    def test_len_and_bool(self) -> None:
        b = OrderBuilder(_customer(), FlatPricing())
        self.assertEqual(len(b), 0)
        self.assertFalse(b)
        b.add("EL-1001", 1, Money(1))
        self.assertEqual(len(b), 1)
        self.assertTrue(b)


class OrderLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.log = OrderLog()

    def test_starts_empty(self) -> None:
        self.assertEqual(len(self.log), 0)
        self.assertEqual(list(self.log), [])

    def test_record_appends_in_order(self) -> None:
        a, b = _order("ORD-1"), _order("ORD-2")
        self.log.record(a)
        self.log.record(b)
        self.assertEqual(len(self.log), 2)
        self.assertIs(self.log[0], a)
        self.assertIs(self.log[1], b)

    def test_record_non_order_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.log.record("ORD-1")  # type: ignore[arg-type]

    def test_record_duplicate_id_rejected(self) -> None:
        self.log.record(_order("ORD-1"))
        with self.assertRaises(DuplicateEntityError) as ctx:
            self.log.record(_order("ORD-1"))
        self.assertEqual(ctx.exception.key, "ORD-1")
        self.assertEqual(len(self.log), 1)

    def test_getitem_negative_index(self) -> None:
        self.log.record(_order("ORD-1"))
        self.log.record(_order("ORD-2"))
        self.assertEqual(self.log[-1].order_id, "ORD-2")

    def test_getitem_out_of_range_raises_index_error(self) -> None:
        with self.assertRaises(IndexError):
            self.log[0]

    def test_iter_yields_in_insertion_order(self) -> None:
        self.log.record(_order("ORD-2"))
        self.log.record(_order("ORD-1"))
        self.assertEqual([o.order_id for o in self.log], ["ORD-2", "ORD-1"])

    def test_iter_is_generator_snapshot_taken_on_first_next(self) -> None:
        # __iter__ is a generator (yield from list(...)), so the copy happens on first next().
        self.log.record(_order("ORD-1"))
        it = iter(self.log)
        self.log.record(_order("ORD-2"))
        self.assertEqual([o.order_id for o in it], ["ORD-1", "ORD-2"])

    def test_iter_snapshot_isolated_after_first_next(self) -> None:
        self.log.record(_order("ORD-1"))
        self.log.record(_order("ORD-2"))
        it = iter(self.log)
        first = next(it)
        self.log.record(_order("ORD-3"))
        self.assertEqual(first.order_id, "ORD-1")
        self.assertEqual([o.order_id for o in it], ["ORD-2"])

    def test_by_status_filters(self) -> None:
        a, b, c = _order("ORD-1"), _order("ORD-2"), _order("ORD-3")
        for o in (a, b, c):
            self.log.record(o)
        b.advance(OrderStatus.CANCELLED)
        c.advance(OrderStatus.RESERVED)
        self.assertEqual([o.order_id for o in self.log.by_status(OrderStatus.NEW)], ["ORD-1"])
        self.assertEqual([o.order_id for o in self.log.by_status(OrderStatus.CANCELLED)], ["ORD-2"])
        self.assertEqual([o.order_id for o in self.log.by_status(OrderStatus.RESERVED)], ["ORD-3"])
        self.assertEqual(list(self.log.by_status(OrderStatus.SHIPPED)), [])

    def test_by_status_is_lazy_generator(self) -> None:
        gen = self.log.by_status(OrderStatus.NEW)
        self.assertFalse(hasattr(gen, "__len__"))
        self.assertEqual(list(gen), [])

    def test_by_status_non_status_raises_on_first_next(self) -> None:
        gen = self.log.by_status("new")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            next(gen)


if __name__ == "__main__":
    unittest.main()
