"""Trading domain events."""

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent


@dataclass(frozen=True)
class PositionOpened(DomainEvent):
    """Emitted when a position is successfully opened."""

    event_type: str = "PositionOpened"


@dataclass(frozen=True)
class PositionClosed(DomainEvent):
    """Emitted when a position is successfully closed."""

    event_type: str = "PositionClosed"


@dataclass(frozen=True)
class CircuitBreakerTriggered(DomainEvent):
    """Emitted when circuit breaker activates due to loss threshold."""

    event_type: str = "CircuitBreakerTriggered"


@dataclass(frozen=True)
class EmergencyClose(DomainEvent):
    """Emitted when position is forcefully closed due to risk."""

    event_type: str = "EmergencyClose"


@dataclass(frozen=True)
class BlackSwanDetected(DomainEvent):
    """Emitted when extreme volatility is detected."""

    event_type: str = "BlackSwanDetected"
