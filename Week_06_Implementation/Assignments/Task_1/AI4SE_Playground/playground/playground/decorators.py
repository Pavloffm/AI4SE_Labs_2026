"""Reusable decorators for the playground package."""

from __future__ import annotations

import functools
from typing import Callable, List, Tuple, TypeVar

T = TypeVar("T")


class AuditTrail:
    """Class-based decorator recording call outcomes into an in-memory list.

    When applied it wraps a callable so that, after each invocation, an entry
    such as ``"<label>:<func_name>:ok"`` (or ``:error:<ExcName>`` on failure)
    is appended to an internal list. Entries are retrievable via
    :attr:`entries` and the trail can be reset with :meth:`clear`.
    """

    def __init__(self, label: str = "audit") -> None:
        """Initialise the trail with a non-empty string ``label``."""
        if not isinstance(label, str):
            raise TypeError("label must be str")
        if label.strip() == "":
            raise ValueError("label required")
        self._label = label
        self._entries: List[str] = []

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorate ``func``; returns a wrapped callable."""
        if not callable(func):
            raise TypeError("func must be callable")
        label = self._label
        entries = self._entries

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> T:
            """Invoke the wrapped function and record the outcome."""
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                entries.append(f"{label}:{func.__name__}:error:{type(exc).__name__}")
                raise
            entries.append(f"{label}:{func.__name__}:ok")
            return result

        return wrapper

    @property
    def entries(self) -> Tuple[str, ...]:
        """Immutable snapshot of recorded entries."""
        return tuple(self._entries)

    def clear(self) -> None:
        """Remove all recorded entries."""
        self._entries.clear()

    def __len__(self) -> int:
        """Return the number of recorded entries."""
        return len(self._entries)
