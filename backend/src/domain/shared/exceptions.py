class DomainException(Exception):
    """Base exception for domain rule violations."""


class InsufficientBalance(DomainException):
    """Raised when available balance cannot satisfy position sizing."""


class CircuitBreakerActive(DomainException):
    """Raised when trading should be blocked by risk controls."""


class RiskCheckFailed(DomainException):
    """Raised when trade validation rejects an order."""


class InvalidPosition(DomainException):
    """Raised when position state is inconsistent."""


class ExchangeError(DomainException):
    """Raised when exchange execution cannot be completed."""


class StopLossPlacementFailed(DomainException):
    """Raised when stop loss cannot be placed after retries."""
