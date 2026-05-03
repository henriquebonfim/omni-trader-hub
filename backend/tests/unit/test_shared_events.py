from __future__ import annotations

import pytest

from src.domain.shared.events import DomainEvent, EventBus


@pytest.mark.asyncio
async def test_event_bus_calls_typed_subscriber() -> None:
    bus = EventBus()
    received: list[str] = []

    async def on_position_opened(event: DomainEvent) -> None:
        received.append(event.event_type)

    bus.subscribe("PositionOpened", on_position_opened)

    await bus.publish(DomainEvent(event_type="PositionOpened"))

    assert received == ["PositionOpened"]


@pytest.mark.asyncio
async def test_event_bus_calls_global_subscriber_for_any_event() -> None:
    bus = EventBus()
    received: list[str] = []

    async def on_any(event: DomainEvent) -> None:
        received.append(event.event_type)

    bus.subscribe_all(on_any)

    await bus.publish(DomainEvent(event_type="PositionOpened"))
    await bus.publish(DomainEvent(event_type="PositionClosed"))

    assert received == ["PositionOpened", "PositionClosed"]


@pytest.mark.asyncio
async def test_event_bus_calls_typed_and_global_subscribers() -> None:
    bus = EventBus()
    typed: list[str] = []
    global_events: list[str] = []

    async def on_typed(event: DomainEvent) -> None:
        typed.append(event.event_type)

    async def on_all(event: DomainEvent) -> None:
        global_events.append(event.event_type)

    bus.subscribe("CircuitBreakerTriggered", on_typed)
    bus.subscribe_all(on_all)

    await bus.publish(DomainEvent(event_type="CircuitBreakerTriggered"))

    assert typed == ["CircuitBreakerTriggered"]
    assert global_events == ["CircuitBreakerTriggered"]
