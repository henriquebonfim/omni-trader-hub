from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    """Trading side value object."""

    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class Price:
    """Positive monetary price."""

    value: float

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Price must be greater than 0")

    def __float__(self) -> float:
        return float(self.value)


@dataclass(frozen=True)
class Size:
    """Positive order/position size."""

    value: float

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Size must be greater than 0")

    def __float__(self) -> float:
        return float(self.value)

    def __mul__(self, other: float) -> float:
        """Multiply size by a number, returning float."""
        return float(self.value) * float(other)

    def __rmul__(self, other: float) -> float:
        """Right multiply size by a number, returning float."""
        return float(other) * float(self.value)


@dataclass(frozen=True)
class Leverage:
    """Exchange leverage, clamped to a practical futures range."""

    value: float

    def __post_init__(self) -> None:
        if not 1 <= self.value <= 125:
            raise ValueError("Leverage must be between 1 and 125")

    def __float__(self) -> float:
        return float(self.value)


@dataclass(frozen=True)
class PnL:
    """Signed profit-and-loss amount."""

    value: float

    def __float__(self) -> float:
        return float(self.value)


@dataclass(frozen=True)
class Percentage:
    """Percentage value represented in [0, 100]."""

    value: float

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError("Percentage must be between 0 and 100")

    def __float__(self) -> float:
        return float(self.value)
