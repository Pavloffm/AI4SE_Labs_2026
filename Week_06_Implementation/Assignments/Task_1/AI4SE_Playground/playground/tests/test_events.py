"""Unit tests for the events module."""
from __future__ import annotations

import unittest
from typing import List, Mapping

from playground.enums import EventType
from playground.events import EventBus


class EventBusSubscribeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = EventBus()

    def test_starts_empty(self) -> None:
        self.assertEqual(len(self.bus), 0)
        self.assertNotIn(EventType.STOCK_ADDED, self.bus)

    def test_subscribe_registers_handler(self) -> None:
        self.bus.subscribe(EventType.STOCK_ADDED, lambda p: None)
        self.assertEqual(len(self.bus), 1)
        self.assertIn(EventType.STOCK_ADDED, self.bus)

    def test_subscribe_non_event_type_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.bus.subscribe(1, lambda p: None)  # type: ignore[arg-type]

    def test_subscribe_non_callable_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.bus.subscribe(EventType.STOCK_ADDED, "not callable")  # type: ignore[arg-type]

    def test_same_handler_twice_counted_twice(self) -> None:
        def h(p: Mapping[str, object]) -> None:
            pass

        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.assertEqual(len(self.bus), 2)

    def test_len_sums_across_types(self) -> None:
        self.bus.subscribe(EventType.STOCK_ADDED, lambda p: None)
        self.bus.subscribe(EventType.ORDER_SHIPPED, lambda p: None)
        self.bus.subscribe(EventType.ORDER_SHIPPED, lambda p: None)
        self.assertEqual(len(self.bus), 3)


class EventBusUnsubscribeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = EventBus()

    def test_unsubscribe_registered_returns_true(self) -> None:
        def h(p: Mapping[str, object]) -> None:
            pass

        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.assertTrue(self.bus.unsubscribe(EventType.STOCK_ADDED, h))
        self.assertEqual(len(self.bus), 0)

    def test_unsubscribe_unknown_handler_returns_false(self) -> None:
        self.assertFalse(self.bus.unsubscribe(EventType.STOCK_ADDED, lambda p: None))

    def test_unsubscribe_wrong_type_returns_false(self) -> None:
        def h(p: Mapping[str, object]) -> None:
            pass

        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.assertFalse(self.bus.unsubscribe(EventType.ORDER_SHIPPED, h))
        self.assertEqual(len(self.bus), 1)

    def test_unsubscribe_removes_first_occurrence_only(self) -> None:
        calls: List[str] = []

        def h(p: Mapping[str, object]) -> None:
            calls.append("h")

        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.bus.subscribe(EventType.STOCK_ADDED, h)
        self.assertTrue(self.bus.unsubscribe(EventType.STOCK_ADDED, h))
        self.assertEqual(len(self.bus), 1)
        self.bus.publish(EventType.STOCK_ADDED, {})
        self.assertEqual(calls, ["h"])

    def test_unsubscribe_on_unknown_type_returns_false(self) -> None:
        self.assertFalse(self.bus.unsubscribe(EventType.ORDER_CANCELLED, lambda p: None))


class EventBusPublishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bus = EventBus()
        self.received: List[Mapping[str, object]] = []

    def test_publish_no_handlers_returns_zero(self) -> None:
        self.assertEqual(self.bus.publish(EventType.STOCK_ADDED, {}), 0)

    def test_publish_calls_handler_with_payload(self) -> None:
        self.bus.subscribe(EventType.STOCK_ADDED, self.received.append)
        payload = {"sku": "EL-1001"}
        self.assertEqual(self.bus.publish(EventType.STOCK_ADDED, payload), 1)
        self.assertEqual(self.received, [payload])

    def test_publish_only_matching_type(self) -> None:
        self.bus.subscribe(EventType.STOCK_ADDED, self.received.append)
        self.bus.publish(EventType.ORDER_SHIPPED, {"x": 1})
        self.assertEqual(self.received, [])

    def test_handlers_called_in_subscription_order(self) -> None:
        order: List[str] = []
        self.bus.subscribe(EventType.STOCK_ADDED, lambda p: order.append("first"))
        self.bus.subscribe(EventType.STOCK_ADDED, lambda p: order.append("second"))
        self.assertEqual(self.bus.publish(EventType.STOCK_ADDED, {}), 2)
        self.assertEqual(order, ["first", "second"])

    def test_publish_non_event_type_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.bus.publish("STOCK_ADDED", {})  # type: ignore[arg-type]

    def test_publish_non_mapping_payload_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.bus.publish(EventType.STOCK_ADDED, ["x"])  # type: ignore[arg-type]

    def test_publish_accepts_any_mapping(self) -> None:
        from types import MappingProxyType

        self.bus.subscribe(EventType.STOCK_ADDED, self.received.append)
        self.bus.publish(EventType.STOCK_ADDED, MappingProxyType({"a": 1}))
        self.assertEqual(len(self.received), 1)

    def test_handler_exception_propagates(self) -> None:
        def boom(p: Mapping[str, object]) -> None:
            raise RuntimeError("handler failed")

        self.bus.subscribe(EventType.STOCK_ADDED, boom)
        with self.assertRaises(RuntimeError):
            self.bus.publish(EventType.STOCK_ADDED, {})

    def test_handler_unsubscribing_during_publish_does_not_skip(self) -> None:
        calls: List[str] = []

        def first(p: Mapping[str, object]) -> None:
            calls.append("first")
            self.bus.unsubscribe(EventType.STOCK_ADDED, first)

        def second(p: Mapping[str, object]) -> None:
            calls.append("second")

        self.bus.subscribe(EventType.STOCK_ADDED, first)
        self.bus.subscribe(EventType.STOCK_ADDED, second)
        self.assertEqual(self.bus.publish(EventType.STOCK_ADDED, {}), 2)
        self.assertEqual(calls, ["first", "second"])


class EventBusContainsTests(unittest.TestCase):
    def test_contains_false_without_handlers(self) -> None:
        self.assertNotIn(EventType.ORDER_SHIPPED, EventBus())

    def test_contains_true_with_handler(self) -> None:
        bus = EventBus()
        bus.subscribe(EventType.ORDER_SHIPPED, lambda p: None)
        self.assertIn(EventType.ORDER_SHIPPED, bus)

    def test_contains_false_after_all_unsubscribed(self) -> None:
        bus = EventBus()

        def h(p: Mapping[str, object]) -> None:
            pass

        bus.subscribe(EventType.ORDER_SHIPPED, h)
        bus.unsubscribe(EventType.ORDER_SHIPPED, h)
        self.assertNotIn(EventType.ORDER_SHIPPED, bus)

    def test_contains_non_event_type_is_false(self) -> None:
        self.assertNotIn("ORDER_SHIPPED", EventBus())
        self.assertNotIn(4, EventBus())


if __name__ == "__main__":
    unittest.main()
