"""General-purpose helpers shared across the playground package."""

from __future__ import annotations

import string
from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")

_SKU_ALLOWED = frozenset(string.ascii_uppercase + string.digits + "-")


def normalize_sku(raw: str) -> str:
    """Validate and normalise a SKU string.

    The value must be a :class:`str` of 3..16 characters containing only
    uppercase ASCII letters, digits, or hyphens; leading/trailing whitespace
    is stripped and the result is uppercased.

    Raises:
        TypeError: if ``raw`` is not a string.
        ValueError: if the length is out of range or contains invalid chars.
    """
    if not isinstance(raw, str):
        raise TypeError("sku must be str")
    s = raw.strip().upper()
    if not (3 <= len(s) <= 16):
        raise ValueError("sku length must be 3..16")
    for ch in s:
        if ch not in _SKU_ALLOWED:
            raise ValueError("invalid sku characters")
    return s


def format_cents(cents: int) -> str:
    """Render an integer cent amount as a ``$X.YY`` string."""
    if isinstance(cents, bool) or not isinstance(cents, int):
        raise TypeError("cents must be int")
    if cents < 0:
        raise ValueError("cents cannot be negative")
    return f"${cents // 100}.{cents % 100:02d}"


def ensure_positive_int(value: object, name: str) -> int:
    """Coerce ``value`` to a strictly positive ``int``.

    ``name`` is used in the error message to identify the parameter.

    Raises:
        TypeError: if ``value`` is a boolean or not an ``int``.
        ValueError: if ``value`` is not greater than zero.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be int")
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def chunked(items: Iterable[T], size: int) -> Iterator[List[T]]:
    """Yield successive ``size``-item lists from ``items``.

    The final batch may contain fewer than ``size`` items. The last (possibly
    empty) partial batch is only yielded when non-empty.

    Raises:
        TypeError/ValueError: propagated from :func:`ensure_positive_int`.
    """
    size = ensure_positive_int(size, "size")
    batch: List[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
