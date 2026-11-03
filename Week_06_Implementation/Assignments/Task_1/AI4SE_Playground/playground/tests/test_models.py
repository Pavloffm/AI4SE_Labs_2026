"""Unit tests for the models module."""
from __future__ import annotations

import unittest

from playground.base import Entity
from playground.enums import Category
from playground.models import Customer, LineItem, Money, Product


class MoneyConstructionTests(unittest.TestCase):
    def test_default_is_zero(self) -> None:
        self.assertEqual(Money().cents, 0)

    def test_stores_cents(self) -> None:
        self.assertEqual(Money(1234).cents, 1234)

    def test_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money(True)  # type: ignore[arg-type]

    def test_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money(1.5)  # type: ignore[arg-type]

    def test_str_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money("100")  # type: ignore[arg-type]

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Money(-1)
        self.assertEqual(str(ctx.exception), "money cannot be negative")

    def test_cents_is_read_only(self) -> None:
        m = Money(5)
        with self.assertRaises(AttributeError):
            m.cents = 10  # type: ignore[misc]


class MoneyArithmeticTests(unittest.TestCase):
    def test_add(self) -> None:
        self.assertEqual(Money(100) + Money(250), Money(350))

    def test_add_non_money_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Money(1) + 1  # type: ignore[operator]

    def test_sub(self) -> None:
        self.assertEqual(Money(500) - Money(120), Money(380))

    def test_sub_to_zero_allowed(self) -> None:
        self.assertEqual(Money(5) - Money(5), Money(0))

    def test_sub_non_money_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Money(5) - 1  # type: ignore[operator]

    def test_sub_negative_result_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Money(1) - Money(2)
        self.assertEqual(str(ctx.exception), "subtraction would be negative")

    def test_mul_by_int(self) -> None:
        self.assertEqual(Money(250) * 3, Money(750))

    def test_mul_by_zero(self) -> None:
        self.assertEqual(Money(250) * 0, Money(0))

    def test_mul_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money(5) * True  # type: ignore[operator]

    def test_mul_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money(5) * 1.5  # type: ignore[operator]

    def test_mul_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Money(5) * -1

    def test_rmul_supports_int_on_left(self) -> None:
        self.assertEqual(3 * Money(250), Money(750))

    def test_rmul_delegates_to_mul(self) -> None:
        self.assertEqual(Money(4).__rmul__(2), Money(4).__mul__(2))

    def test_rmul_invalid_factor_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Money(4).__rmul__(True)  # type: ignore[arg-type]


class MoneyComparisonTests(unittest.TestCase):
    def test_eq_same_cents(self) -> None:
        self.assertTrue(Money(10) == Money(10))

    def test_eq_different_cents(self) -> None:
        self.assertFalse(Money(10) == Money(11))

    def test_eq_non_money_is_false(self) -> None:
        self.assertFalse(Money(10) == 10)
        self.assertFalse(Money(0) == None)  # noqa: E711

    def test_eq_non_money_returns_not_implemented(self) -> None:
        self.assertIs(Money(1).__eq__(1), NotImplemented)

    def test_ne(self) -> None:
        self.assertTrue(Money(1) != Money(2))
        self.assertFalse(Money(2) != Money(2))

    def test_lt_true(self) -> None:
        self.assertTrue(Money(1) < Money(2))

    def test_lt_false_when_equal_or_greater(self) -> None:
        self.assertFalse(Money(2) < Money(2))
        self.assertFalse(Money(3) < Money(2))

    def test_lt_non_money_raises_type_error_via_operator(self) -> None:
        with self.assertRaises(TypeError):
            Money(1) < 2  # type: ignore[operator]

    def test_lt_non_money_returns_not_implemented(self) -> None:
        self.assertIs(Money(1).__lt__(2), NotImplemented)

    def test_gt_works_via_reflected_lt(self) -> None:
        # DESIGN.md defines only __lt__; '>' resolves through Python's reflection.
        self.assertTrue(Money(5) > Money(2))
        self.assertFalse(Money(2) > Money(2))

    def test_le_less(self) -> None:
        self.assertTrue(Money(1) <= Money(2))

    def test_le_equal(self) -> None:
        self.assertTrue(Money(2) <= Money(2))

    def test_le_greater(self) -> None:
        self.assertFalse(Money(3) <= Money(2))

    def test_le_non_money_returns_not_implemented(self) -> None:
        self.assertIs(Money(1).__le__(2), NotImplemented)

    def test_le_non_money_raises_type_error_via_operator(self) -> None:
        with self.assertRaises(TypeError):
            Money(1) <= 2  # type: ignore[operator]

    def test_ge_works_via_reflected_le(self) -> None:
        # With __le__ defined, '>=' resolves through Python's reflection.
        self.assertTrue(Money(2) >= Money(2))
        self.assertFalse(Money(1) >= Money(2))

    def test_sorting(self) -> None:
        values = [Money(30), Money(10), Money(20)]
        self.assertEqual([m.cents for m in sorted(values)], [10, 20, 30])


class MoneyMiscTests(unittest.TestCase):
    def test_hash_matches_equal_values(self) -> None:
        self.assertEqual(hash(Money(7)), hash(Money(7)))
        self.assertEqual(hash(Money(7)), hash(("Money", 7)))

    def test_usable_as_set_member(self) -> None:
        self.assertEqual(len({Money(1), Money(1), Money(2)}), 2)

    def test_repr(self) -> None:
        self.assertEqual(repr(Money(1234)), "Money(1234)")

    def test_str_formats_dollars(self) -> None:
        self.assertEqual(str(Money(1234)), "$12.34")
        self.assertEqual(str(Money(0)), "$0.00")

    def test_bool_false_for_zero(self) -> None:
        self.assertFalse(bool(Money(0)))

    def test_bool_true_for_nonzero(self) -> None:
        self.assertTrue(bool(Money(1)))


class ProductTests(unittest.TestCase):
    def _make(self, **overrides: object) -> Product:
        args = {
            "sku": "EL-1001",
            "name": "Headphones",
            "category": Category.ELECTRONICS,
            "unit_price": Money(2500),
        }
        args.update(overrides)
        return Product(**args)  # type: ignore[arg-type]

    def test_is_entity(self) -> None:
        self.assertIsInstance(self._make(), Entity)

    def test_constructor_stores_fields(self) -> None:
        p = self._make()
        self.assertEqual(p.sku, "EL-1001")
        self.assertEqual(p.name, "Headphones")
        self.assertIs(p.category, Category.ELECTRONICS)
        self.assertEqual(p.unit_price, Money(2500))

    def test_sku_is_normalized(self) -> None:
        self.assertEqual(self._make(sku=" el-1001 ").sku, "EL-1001")

    def test_invalid_sku_propagates_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self._make(sku="x")

    def test_non_str_sku_propagates_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self._make(sku=123)

    def test_non_str_name_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self._make(name=None)
        self.assertEqual(str(ctx.exception), "name required")

    def test_blank_name_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._make(name="   ")

    def test_non_category_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self._make(category="electronics")

    def test_non_money_price_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self._make(unit_price=2500)

    def test_read_only_properties(self) -> None:
        p = self._make()
        with self.assertRaises(AttributeError):
            p.sku = "X"  # type: ignore[misc]

    def test_identity_is_sku(self) -> None:
        self.assertEqual(self._make().identity(), "EL-1001")

    def test_equality_by_identity_same_sku_different_name(self) -> None:
        self.assertEqual(self._make(), self._make(name="Other"))

    def test_inequality_different_sku(self) -> None:
        self.assertNotEqual(self._make(), self._make(sku="GR-2001"))

    def test_with_price_returns_new_product(self) -> None:
        original = self._make()
        updated = original.with_price(Money(999))
        self.assertIsNot(updated, original)
        self.assertEqual(updated.unit_price, Money(999))
        self.assertEqual(original.unit_price, Money(2500))
        self.assertEqual(updated.sku, original.sku)
        self.assertEqual(updated.name, original.name)
        self.assertIs(updated.category, original.category)

    def test_with_price_non_money_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self._make().with_price(999)  # type: ignore[arg-type]

    def test_from_dict_with_category_string(self) -> None:
        p = Product.from_dict(
            {
                "sku": "gr-2001",
                "name": "Beans",
                "category": "Grocery",
                "unit_price_cents": 300,
            }
        )
        self.assertEqual(p.sku, "GR-2001")
        self.assertIs(p.category, Category.GROCERY)
        self.assertEqual(p.unit_price, Money(300))

    def test_from_dict_with_category_enum(self) -> None:
        p = Product.from_dict(
            {
                "sku": "HW-3001",
                "name": "Hammer",
                "category": Category.HARDWARE,
                "unit_price_cents": 1200,
            }
        )
        self.assertIs(p.category, Category.HARDWARE)

    def test_from_dict_missing_key_raises_key_error(self) -> None:
        base = {"sku": "HW-3001", "name": "Hammer", "category": "hardware", "unit_price_cents": 1}
        for key in ("sku", "name", "category", "unit_price_cents"):
            data = dict(base)
            del data[key]
            with self.subTest(missing=key):
                with self.assertRaises(KeyError) as ctx:
                    Product.from_dict(data)
                self.assertEqual(ctx.exception.args[0], key)

    def test_from_dict_bad_category_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Product.from_dict(
                {"sku": "HW-3001", "name": "Hammer", "category": 5, "unit_price_cents": 1}
            )

    def test_from_dict_unknown_category_label_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            Product.from_dict(
                {"sku": "HW-3001", "name": "Hammer", "category": "toys", "unit_price_cents": 1}
            )

    def test_from_dict_invalid_price_propagates(self) -> None:
        with self.assertRaises(ValueError):
            Product.from_dict(
                {"sku": "HW-3001", "name": "Hammer", "category": "hardware", "unit_price_cents": -1}
            )
        with self.assertRaises(TypeError):
            Product.from_dict(
                {"sku": "HW-3001", "name": "Hammer", "category": "hardware", "unit_price_cents": 1.0}
            )

    def test_is_valid_name_accepts_normal(self) -> None:
        self.assertTrue(Product.is_valid_name("Hammer"))

    def test_is_valid_name_rejects_non_str(self) -> None:
        self.assertFalse(Product.is_valid_name(None))  # type: ignore[arg-type]
        self.assertFalse(Product.is_valid_name(42))  # type: ignore[arg-type]

    def test_is_valid_name_rejects_blank(self) -> None:
        self.assertFalse(Product.is_valid_name(""))
        self.assertFalse(Product.is_valid_name("   "))

    def test_is_valid_name_length_boundaries(self) -> None:
        self.assertTrue(Product.is_valid_name("x"))
        self.assertTrue(Product.is_valid_name("x" * 80))
        self.assertFalse(Product.is_valid_name("x" * 81))

    def test_is_valid_name_strips_before_measuring(self) -> None:
        self.assertTrue(Product.is_valid_name("  " + "x" * 80 + "  "))


class LineItemTests(unittest.TestCase):
    def test_stores_fields(self) -> None:
        li = LineItem("el-1001", 2, Money(250))
        self.assertEqual(li.sku, "EL-1001")
        self.assertEqual(li.quantity, 2)
        self.assertEqual(li.unit_price, Money(250))

    def test_subtotal(self) -> None:
        self.assertEqual(LineItem("EL-1001", 4, Money(250)).subtotal, Money(1000))

    def test_invalid_sku_propagates(self) -> None:
        with self.assertRaises(ValueError):
            LineItem("a", 1, Money(1))

    def test_bool_quantity_rejected(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            LineItem("EL-1001", True, Money(1))  # type: ignore[arg-type]
        self.assertEqual(str(ctx.exception), "quantity must be int")

    def test_zero_quantity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            LineItem("EL-1001", 0, Money(1))

    def test_negative_quantity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            LineItem("EL-1001", -1, Money(1))

    def test_non_money_price_rejected(self) -> None:
        with self.assertRaises(TypeError):
            LineItem("EL-1001", 1, 100)  # type: ignore[arg-type]

    def test_with_quantity_returns_new_item(self) -> None:
        original = LineItem("EL-1001", 1, Money(250))
        updated = original.with_quantity(5)
        self.assertIsNot(updated, original)
        self.assertEqual(updated.quantity, 5)
        self.assertEqual(original.quantity, 1)
        self.assertEqual(updated.unit_price, Money(250))

    def test_with_quantity_validates(self) -> None:
        with self.assertRaises(ValueError):
            LineItem("EL-1001", 1, Money(1)).with_quantity(0)
        with self.assertRaises(TypeError):
            LineItem("EL-1001", 1, Money(1)).with_quantity(1.0)  # type: ignore[arg-type]

    def test_eq_same_fields(self) -> None:
        self.assertTrue(LineItem("EL-1001", 1, Money(5)) == LineItem("el-1001", 1, Money(5)))

    def test_eq_differs_on_quantity(self) -> None:
        self.assertFalse(LineItem("EL-1001", 1, Money(5)) == LineItem("EL-1001", 2, Money(5)))

    def test_eq_differs_on_price(self) -> None:
        self.assertFalse(LineItem("EL-1001", 1, Money(5)) == LineItem("EL-1001", 1, Money(6)))

    def test_eq_non_line_item_returns_not_implemented(self) -> None:
        li = LineItem("EL-1001", 1, Money(5))
        self.assertIs(li.__eq__("EL-1001"), NotImplemented)
        self.assertFalse(li == "EL-1001")

    def test_hash_consistent_with_equal_items(self) -> None:
        a = LineItem("EL-1001", 1, Money(5))
        b = LineItem("EL-1001", 1, Money(5))
        self.assertEqual(hash(a), hash(b))
        self.assertEqual(hash(a), hash(("EL-1001", 1)))

    def test_repr(self) -> None:
        self.assertEqual(
            repr(LineItem("EL-1001", 2, Money(250))),
            "LineItem('EL-1001', 2, Money(250))",
        )


class CustomerTests(unittest.TestCase):
    def test_default_credit_limit_and_balance(self) -> None:
        c = Customer("C-1", "Alice")
        self.assertEqual(c.credit_limit, Money(0))
        self.assertEqual(c.balance, Money(0))

    def test_constructor_stores_fields(self) -> None:
        c = Customer("C-1", "Alice", Money(1000))
        self.assertEqual(c.customer_id, "C-1")
        self.assertEqual(c.name, "Alice")
        self.assertEqual(c.credit_limit, Money(1000))
        self.assertIsInstance(c, Entity)

    def test_default_limit_not_shared_across_instances_semantics(self) -> None:
        # Money is immutable, so the shared default is safe; verify value semantics.
        self.assertEqual(Customer("C-1", "A").credit_limit, Customer("C-2", "B").credit_limit)

    def test_empty_customer_id_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Customer("   ", "Alice")
        self.assertEqual(str(ctx.exception), "customer_id required")

    def test_non_str_customer_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Customer(None, "Alice")  # type: ignore[arg-type]

    def test_empty_name_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            Customer("C-1", "")
        self.assertEqual(str(ctx.exception), "name required")

    def test_non_str_name_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Customer("C-1", 5)  # type: ignore[arg-type]

    def test_non_money_credit_limit_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Customer("C-1", "Alice", 1000)  # type: ignore[arg-type]

    def test_identity_is_customer_id(self) -> None:
        self.assertEqual(Customer("C-9", "Z").identity(), "C-9")

    def test_equality_by_customer_id(self) -> None:
        self.assertEqual(Customer("C-1", "A"), Customer("C-1", "B"))
        self.assertNotEqual(Customer("C-1", "A"), Customer("C-2", "A"))

    def test_can_afford_true_within_limit(self) -> None:
        c = Customer("C-1", "A", Money(1000))
        self.assertTrue(c.can_afford(Money(1000)))

    def test_can_afford_false_over_limit(self) -> None:
        c = Customer("C-1", "A", Money(1000))
        self.assertFalse(c.can_afford(Money(1001)))

    def test_can_afford_accounts_for_existing_balance(self) -> None:
        c = Customer("C-1", "A", Money(1000))
        c.charge(Money(600))
        self.assertTrue(c.can_afford(Money(400)))
        self.assertFalse(c.can_afford(Money(401)))

    def test_can_afford_non_money_rejected(self) -> None:
        with self.assertRaises(TypeError):
            Customer("C-1", "A", Money(1)).can_afford(1)  # type: ignore[arg-type]

    def test_charge_increases_balance(self) -> None:
        c = Customer("C-1", "A", Money(1000))
        c.charge(Money(300))
        self.assertEqual(c.balance, Money(300))
        c.charge(Money(200))
        self.assertEqual(c.balance, Money(500))

    def test_charge_exceeding_limit_raises_and_keeps_balance(self) -> None:
        c = Customer("C-1", "A", Money(100))
        with self.assertRaises(ValueError) as ctx:
            c.charge(Money(101))
        self.assertEqual(str(ctx.exception), "credit limit exceeded")
        self.assertEqual(c.balance, Money(0))

    def test_charge_exactly_to_limit_allowed(self) -> None:
        c = Customer("C-1", "A", Money(100))
        c.charge(Money(100))
        self.assertEqual(c.balance, Money(100))

    def test_charge_non_money_propagates_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Customer("C-1", "A", Money(100)).charge(5)  # type: ignore[arg-type]

    def test_read_only_properties(self) -> None:
        c = Customer("C-1", "A")
        with self.assertRaises(AttributeError):
            c.balance = Money(5)  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
