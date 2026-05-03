from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event published across bounded contexts."""

    event_type: str
    payload: dict[str, object] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """In-process async event bus for decoupling cross-context side effects."""

    def __init__(self) -> None:
        self._typed_subscribers: dict[str, list[EventHandler]] = {}
        self._all_subscribers: list[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._typed_subscribers.setdefault(event_type, []).append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._all_subscribers.append(handler)

    async def publish(self, event: DomainEvent) -> None:
        typed = self._typed_subscribers.get(event.event_type, [])
        handlers = [*typed, *self._all_subscribers]
        if not handlers:
            return
        await asyncio.gather(*(handler(event) for handler in handlers))
