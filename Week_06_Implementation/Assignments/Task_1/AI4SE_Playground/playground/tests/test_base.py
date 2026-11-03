"""Unit tests for the base module."""
from __future__ import annotations

import unittest
from typing import Dict, Iterator, Sequence

from playground.base import Entity, PricingStrategy, Repository
from playground.models import LineItem, Money


class _Thing(Entity):
    def __init__(self, key: str) -> None:
        self._key = key

    def identity(self) -> str:
        return self._key


class _OtherThing(Entity):
    def __init__(self, key: str) -> None:
        self._key = key

    def identity(self) -> str:
        return self._key


class EntityTests(unittest.TestCase):
    def test_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Entity()  # type: ignore[abstract]

    def test_subclass_without_identity_is_abstract(self) -> None:
        class Incomplete(Entity):
            pass

        with self.assertRaises(TypeError):
            Incomplete()  # type: ignore[abstract]

    def test_eq_same_type_same_identity(self) -> None:
        self.assertTrue(_Thing("a") == _Thing("a"))

    def test_eq_same_type_different_identity(self) -> None:
        self.assertFalse(_Thing("a") == _Thing("b"))

    def test_eq_different_type_same_identity_is_false(self) -> None:
        # Returns NotImplemented; Python falls back to identity -> False.
        self.assertFalse(_Thing("a") == _OtherThing("a"))

    def test_eq_non_entity_is_false(self) -> None:
        self.assertFalse(_Thing("a") == "a")
        self.assertFalse(_Thing("a") == None)  # noqa: E711

    def test_eq_returns_not_implemented_for_mismatched_type(self) -> None:
        self.assertIs(_Thing("a").__eq__(_OtherThing("a")), NotImplemented)

    def test_ne_uses_identity_comparison(self) -> None:
        self.assertTrue(_Thing("a") != _Thing("b"))
        self.assertFalse(_Thing("a") != _Thing("a"))

    def test_hash_equal_for_equal_entities(self) -> None:
        self.assertEqual(hash(_Thing("a")), hash(_Thing("a")))

    def test_hash_usable_in_set(self) -> None:
        self.assertEqual(len({_Thing("a"), _Thing("a"), _Thing("b")}), 2)

    def test_hash_includes_type_name(self) -> None:
        self.assertEqual(hash(_Thing("a")), hash(("_Thing", "a")))

    def test_repr(self) -> None:
        self.assertEqual(repr(_Thing("abc")), "_Thing('abc')")


class _FlatPricing(PricingStrategy):
    def price(self, items: Sequence[LineItem]) -> Money:
        return self._sum_subtotals(items)


class PricingStrategyTests(unittest.TestCase):
    def test_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            PricingStrategy()  # type: ignore[abstract]

    def test_call_delegates_to_price(self) -> None:
        items = [LineItem("EL-1001", 2, Money(100))]
        strategy = _FlatPricing()
        self.assertEqual(strategy(items), strategy.price(items))
        self.assertEqual(strategy(items), Money(200))

    def test_sum_subtotals_empty_returns_zero_money(self) -> None:
        result = PricingStrategy._sum_subtotals([])
        self.assertIsInstance(result, Money)
        self.assertEqual(result, Money(0))

    def test_sum_subtotals_single_item(self) -> None:
        items = [LineItem("EL-1001", 3, Money(250))]
        self.assertEqual(PricingStrategy._sum_subtotals(items), Money(750))

    def test_sum_subtotals_multiple_items(self) -> None:
        items = [
            LineItem("EL-1001", 2, Money(250)),
            LineItem("GR-2001", 1, Money(300)),
        ]
        self.assertEqual(PricingStrategy._sum_subtotals(items), Money(800))

    def test_sum_subtotals_accepts_tuple(self) -> None:
        items = (LineItem("EL-1001", 1, Money(5)),)
        self.assertEqual(PricingStrategy._sum_subtotals(items), Money(5))


class _DictRepository(Repository):
    def __init__(self) -> None:
        self._data: Dict[str, Entity] = {}

    def add(self, item: Entity) -> None:
        self._data[item.identity()] = item

    def get(self, key: str) -> Entity:
        return self._data[key]

    def remove(self, key: str) -> Entity:
        return self._data.pop(key)

    def __iter__(self) -> Iterator[Entity]:
        return iter(list(self._data.values()))

    def __len__(self) -> int:
        return len(self._data)


class RepositoryTests(unittest.TestCase):
    def test_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            Repository()  # type: ignore[abstract]

    def test_contains_non_str_returns_false(self) -> None:
        repo = _DictRepository()
        repo.add(_Thing("a"))
        self.assertFalse(5 in repo)  # type: ignore[operator]
        self.assertFalse(_Thing("a") in repo)  # type: ignore[operator]

    def test_contains_present_key_is_true(self) -> None:
        repo = _DictRepository()
        repo.add(_Thing("a"))
        self.assertTrue("a" in repo)

    def test_contains_missing_key_is_false_via_keyerror(self) -> None:
        repo = _DictRepository()
        self.assertFalse("missing" in repo)

    def test_contains_uses_get(self) -> None:
        calls = []

        class _Spy(_DictRepository):
            def get(self, key: str) -> Entity:
                calls.append(key)
                return super().get(key)

        repo = _Spy()
        repo.add(_Thing("k"))
        self.assertTrue("k" in repo)
        self.assertEqual(calls, ["k"])


if __name__ == "__main__":
    unittest.main()
