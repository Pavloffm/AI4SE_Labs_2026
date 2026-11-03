"""Unit tests for the repository module."""
from __future__ import annotations

import unittest

from playground.base import Entity, Repository
from playground.exceptions import DuplicateEntityError
from playground.models import Customer, Money, Product
from playground.repository import InMemoryRepository
from playground.enums import Category


class _Item(Entity):
    def __init__(self, key: str) -> None:
        self._key = key

    def identity(self) -> str:
        return self._key


class _Other(Entity):
    def identity(self) -> str:
        return "x"


class InMemoryRepositoryConstructionTests(unittest.TestCase):
    def test_is_repository(self) -> None:
        self.assertIsInstance(InMemoryRepository(Product), Repository)

    def test_non_type_rejected(self) -> None:
        with self.assertRaises(TypeError):
            InMemoryRepository("Product")  # type: ignore[arg-type]

    def test_new_repo_is_empty(self) -> None:
        self.assertEqual(len(InMemoryRepository(_Item)), 0)


class InMemoryRepositoryAddTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryRepository(_Item)

    def test_add_then_get(self) -> None:
        item = _Item("a")
        self.repo.add(item)
        self.assertIs(self.repo.get("a"), item)
        self.assertEqual(len(self.repo), 1)

    def test_add_wrong_type_rejected(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            self.repo.add(_Other())  # type: ignore[arg-type]
        self.assertIn("_Item", str(ctx.exception))

    def test_add_non_entity_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.repo.add("a")  # type: ignore[arg-type]

    def test_add_duplicate_raises(self) -> None:
        self.repo.add(_Item("a"))
        with self.assertRaises(DuplicateEntityError) as ctx:
            self.repo.add(_Item("a"))
        self.assertEqual(ctx.exception.key, "a")
        self.assertEqual(len(self.repo), 1)

    def test_duplicate_check_keeps_original(self) -> None:
        first = _Item("a")
        self.repo.add(first)
        with self.assertRaises(DuplicateEntityError):
            self.repo.add(_Item("a"))
        self.assertIs(self.repo.get("a"), first)

    def test_subclass_instances_accepted(self) -> None:
        class _Sub(_Item):
            pass

        self.repo.add(_Sub("s"))
        self.assertIn("s", self.repo)


class InMemoryRepositoryGetRemoveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryRepository(_Item)
        self.repo.add(_Item("a"))

    def test_get_missing_raises_key_error(self) -> None:
        with self.assertRaises(KeyError) as ctx:
            self.repo.get("zzz")
        self.assertEqual(ctx.exception.args[0], "zzz")

    def test_get_non_str_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.repo.get(1)  # type: ignore[arg-type]

    def test_remove_returns_item_and_deletes(self) -> None:
        removed = self.repo.remove("a")
        self.assertEqual(removed.identity(), "a")
        self.assertNotIn("a", self.repo)
        self.assertEqual(len(self.repo), 0)

    def test_remove_missing_raises_key_error(self) -> None:
        with self.assertRaises(KeyError) as ctx:
            self.repo.remove("missing")
        self.assertEqual(ctx.exception.args[0], "missing")

    def test_remove_then_add_again_succeeds(self) -> None:
        self.repo.remove("a")
        self.repo.add(_Item("a"))
        self.assertEqual(len(self.repo), 1)


class InMemoryRepositoryContainsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = InMemoryRepository(_Item)
        self.repo.add(_Item("a"))

    def test_contains_present(self) -> None:
        self.assertTrue("a" in self.repo)

    def test_contains_absent(self) -> None:
        self.assertFalse("b" in self.repo)

    def test_contains_non_str_is_false(self) -> None:
        self.assertFalse(1 in self.repo)  # type: ignore[operator]
        self.assertFalse(_Item("a") in self.repo)  # type: ignore[operator]

    def test_contains_does_not_use_get(self) -> None:
        # Override path: membership does not raise KeyError internally.
        self.assertFalse("nope" in self.repo)


class InMemoryRepositoryLenIterTests(unittest.TestCase):
    def test_len_counts_items(self) -> None:
        repo = InMemoryRepository(_Item)
        for k in ("c", "a", "b"):
            repo.add(_Item(k))
        self.assertEqual(len(repo), 3)

    def test_iter_sorted_by_key(self) -> None:
        repo = InMemoryRepository(_Item)
        for k in ("c", "a", "b"):
            repo.add(_Item(k))
        self.assertEqual([e.identity() for e in repo], ["a", "b", "c"])

    def test_iter_empty(self) -> None:
        self.assertEqual(list(InMemoryRepository(_Item)), [])

    def test_iter_is_a_generator_over_snapshot_keys(self) -> None:
        repo = InMemoryRepository(_Item)
        repo.add(_Item("a"))
        it = iter(repo)
        repo.add(_Item("b"))
        self.assertEqual([e.identity() for e in it], ["a", "b"])


class InMemoryRepositoryWithProductsTests(unittest.TestCase):
    def test_product_repository_roundtrip(self) -> None:
        repo = InMemoryRepository(Product)
        p = Product("EL-1001", "Headphones", Category.ELECTRONICS, Money(2500))
        repo.add(p)
        self.assertIs(repo.get("EL-1001"), p)
        self.assertIn("EL-1001", repo)

    def test_customer_repository_rejects_product(self) -> None:
        repo = InMemoryRepository(Customer)
        p = Product("EL-1001", "Headphones", Category.ELECTRONICS, Money(2500))
        with self.assertRaises(TypeError):
            repo.add(p)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
