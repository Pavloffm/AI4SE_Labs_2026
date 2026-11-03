"""Core domain models: money, products, line items, and customers."""

from __future__ import annotations

from typing import Mapping

from .base import Entity
from .enums import Category
from .util import ensure_positive_int, format_cents, normalize_sku


class Money:
    """Immutable integer-cents amount."""

    def __init__(self, cents: int = 0) -> None:
        """Create a monetary amount; cents must be a non-negative ``int``."""
        if isinstance(cents, bool) or not isinstance(cents, int):
            raise TypeError("cents must be int")
        if cents < 0:
            raise ValueError("money cannot be negative")
        self._cents = cents

    @property
    def cents(self) -> int:
        """Return the stored cents value."""
        return self._cents

    def __add__(self, other: Money) -> Money:
        """Return a new Money equal to ``self + other``."""
        if not isinstance(other, Money):
            raise TypeError("can only add Money to Money")
        return Money(self._cents + other._cents)

    def __sub__(self, other: Money) -> Money:
        """Return a new Money equal to ``self - other``.

        Raises:
            TypeError: if ``other`` is not :class:`Money`.
            ValueError: if the result would be negative.
        """
        if not isinstance(other, Money):
            raise TypeError("can only subtract Money from Money")
        difference = self._cents - other._cents
        if difference < 0:
            raise ValueError("subtraction would be negative")
        return Money(difference)

    def __mul__(self, factor: int) -> Money:
        """Return ``self`` multiplied by a non-negative integer."""
        if isinstance(factor, bool) or not isinstance(factor, int):
            raise TypeError("factor must be int")
        if factor < 0:
            raise ValueError("factor cannot be negative")
        return Money(self._cents * factor)

    def __rmul__(self, factor: int) -> Money:
        """Support ``factor * Money`` by delegating to :meth:`__mul__`."""
        return self.__mul__(factor)

    def __eq__(self, other: object) -> bool:
        """Return True if ``other`` is Money with equal cents."""
        if not isinstance(other, Money):
            return NotImplemented
        return self._cents == other._cents

    def __lt__(self, other: Money) -> bool:
        """Return True if ``self`` is strictly less than ``other``."""
        if not isinstance(other, Money):
            return NotImplemented
        return self._cents < other._cents

    def __le__(self, other: Money) -> bool:
        """Return True if ``self`` is less than or equal to ``other``."""
        if not isinstance(other, Money):
            return NotImplemented
        return self._cents <= other._cents

    def __hash__(self) -> int:
        """Hash by the type name and cents value."""
        return hash(("Money", self._cents))

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"Money({self._cents})"

    def __str__(self) -> str:
        """Render the amount as a ``$X.YY`` string."""
        return format_cents(self._cents)

    def __bool__(self) -> bool:
        """Return True when the amount is non-zero."""
        return self._cents != 0


class Product(Entity):
    """Catalog item."""

    def __init__(self, sku: str, name: str, category: Category, unit_price: Money) -> None:
        """Create a product after validating its SKU, name, category, and price."""
        sku = normalize_sku(sku)
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("name required")
        if not isinstance(category, Category):
            raise TypeError("category must be Category")
        if not isinstance(unit_price, Money):
            raise TypeError("unit_price must be Money")
        self._sku = sku
        self._name = name
        self._category = category
        self._unit_price = unit_price

    @property
    def sku(self) -> str:
        """Return the product SKU."""
        return self._sku

    @property
    def name(self) -> str:
        """Return the product name."""
        return self._name

    @property
    def category(self) -> Category:
        """Return the product category."""
        return self._category

    @property
    def unit_price(self) -> Money:
        """Return the product unit price."""
        return self._unit_price

    def identity(self) -> str:
        """Return the SKU as the entity identity."""
        return self._sku

    def with_price(self, new_price: Money) -> Product:
        """Return a copy of this product with an updated unit price."""
        if not isinstance(new_price, Money):
            raise TypeError("new_price must be Money")
        return Product(self._sku, self._name, self._category, new_price)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> Product:
        """Build a product from a mapping with keys sku, name, category, unit_price_cents."""
        for key in ("sku", "name", "category", "unit_price_cents"):
            if key not in data:
                raise KeyError(key)
        raw_category = data["category"]
        if isinstance(raw_category, str):
            category = Category.from_label(raw_category)
        elif isinstance(raw_category, Category):
            category = raw_category
        else:
            raise TypeError("category must be str or Category")
        unit_price = Money(data["unit_price_cents"])
        return cls(data["sku"], data["name"], category, unit_price)

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Return True if ``name`` is a string of 1..80 non-blank characters."""
        if not isinstance(name, str):
            return False
        return 1 <= len(name.strip()) <= 80


class LineItem:
    """One SKU with quantity and unit price."""

    def __init__(self, sku: str, quantity: int, unit_price: Money) -> None:
        """Create a line item after validating its SKU, quantity, and price."""
        sku = normalize_sku(sku)
        quantity = ensure_positive_int(quantity, "quantity")
        if not isinstance(unit_price, Money):
            raise TypeError("unit_price must be Money")
        self._sku = sku
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def sku(self) -> str:
        """Return the line item SKU."""
        return self._sku

    @property
    def quantity(self) -> int:
        """Return the line item quantity."""
        return self._quantity

    @property
    def unit_price(self) -> Money:
        """Return the unit price."""
        return self._unit_price

    @property
    def subtotal(self) -> Money:
        """Return the line item subtotal (unit price times quantity)."""
        return self._unit_price * self._quantity

    def with_quantity(self, quantity: int) -> LineItem:
        """Return a copy of this line item with a new quantity."""
        return LineItem(self._sku, quantity, self._unit_price)

    def __eq__(self, other: object) -> bool:
        """Compare SKU, quantity, and unit price for equality."""
        if not isinstance(other, LineItem):
            return NotImplemented
        return (self._sku, self._quantity, self._unit_price) == (
            other._sku,
            other._quantity,
            other._unit_price,
        )

    def __hash__(self) -> int:
        """Hash by SKU and quantity."""
        return hash((self._sku, self._quantity))

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"LineItem({self._sku!r}, {self._quantity}, {self._unit_price!r})"


class Customer(Entity):
    """Buyer with a credit limit. Balance is the amount owed."""

    def __init__(self, customer_id: str, name: str, credit_limit: Money = Money(0)) -> None:
        """Create a customer with the given identity, name, and credit limit."""
        if not isinstance(customer_id, str) or customer_id.strip() == "":
            raise ValueError("customer_id required")
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("name required")
        if not isinstance(credit_limit, Money):
            raise TypeError("credit_limit must be Money")
        self._customer_id = customer_id
        self._name = name
        self._credit_limit = credit_limit
        self._balance = Money(0)

    @property
    def customer_id(self) -> str:
        """Return the customer identity."""
        return self._customer_id

    @property
    def name(self) -> str:
        """Return the customer name."""
        return self._name

    @property
    def credit_limit(self) -> Money:
        """Return the credit limit."""
        return self._credit_limit

    @property
    def balance(self) -> Money:
        """Return the current outstanding balance."""
        return self._balance

    def identity(self) -> str:
        """Return the customer_id as the entity identity."""
        return self._customer_id

    def can_afford(self, total: Money) -> bool:
        """Return True if ``balance + total`` does not exceed the credit limit."""
        if not isinstance(total, Money):
            raise TypeError("total must be Money")
        return self._balance + total <= self._credit_limit

    def charge(self, total: Money) -> None:
        """Increase the balance by ``total``, raising if the limit would be exceeded."""
        if not self.can_afford(total):
            raise ValueError("credit limit exceeded")
        self._balance = self._balance + total
