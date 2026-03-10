from src.shared.domain.aggregate import AggregateRoot
from src.shared.domain.events import DomainEvent


class DummyAggregate(AggregateRoot):
    pass


def test_collect_events_returns_and_clears_buffer() -> None:
    agg = DummyAggregate()
    agg.register_event(DomainEvent(event_type="A"))
    agg.register_event(DomainEvent(event_type="B"))

    first = agg.collect_events()
    second = agg.collect_events()

    assert [event.event_type for event in first] == ["A", "B"]
    assert second == []
