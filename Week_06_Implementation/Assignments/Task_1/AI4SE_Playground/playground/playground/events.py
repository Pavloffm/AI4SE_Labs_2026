"""Synchronous in-process event bus for the playground package."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Callable, Dict, List

from .enums import EventType


class EventBus:
    """Synchronous publish/subscribe keyed by :class:`EventType`."""

    def __init__(self) -> None:
        """Initialise an empty handler registry."""
        self._handlers: Dict[EventType, List[Callable[..., None]]] = {}

    def subscribe(self, event_type: EventType, handler: Callable[..., None]) -> None:
        """Register ``handler`` to be called when ``event_type`` is published."""
        if not isinstance(event_type, EventType):
            raise TypeError("event_type must be EventType")
        if not callable(handler):
            raise TypeError("handler must be callable")
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable[..., None]) -> bool:
        """Remove ``handler`` from ``event_type``; return whether it was present."""
        handlers = self._handlers.get(event_type, [])
        if handler not in handlers:
            return False
        handlers.remove(handler)
        return True

    def publish(self, event_type: EventType, payload: Mapping[str, object]) -> int:
        """Invoke every handler subscribed to ``event_type`` with ``payload``.

        Returns the number of handlers invoked.
        """
        if not isinstance(event_type, EventType):
            raise TypeError("event_type must be EventType")
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a Mapping")
        count = 0
        for handler in list(self._handlers.get(event_type, [])):
            handler(payload)
            count += 1
        return count

    def __len__(self) -> int:
        """Return the total number of registered handlers across all event types."""
        return sum(len(handlers) for handlers in self._handlers.values())

    def __contains__(self, event_type: object) -> bool:
        """Return whether any handlers are registered for ``event_type``."""
        return isinstance(event_type, EventType) and bool(self._handlers.get(event_type))
