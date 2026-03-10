from __future__ import annotations

from typing import List

from .events import DomainEvent


class AggregateRoot:
    """Base aggregate that collects domain events before publishing."""

    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def register_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events
