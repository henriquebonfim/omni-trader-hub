from dataclasses import asdict, dataclass, field
from datetime import date


@dataclass
class DailyStats:
    """Track daily trading statistics."""

    date: date = field(default_factory=date.today)
    starting_balance: float = 0.0
    realized_pnl: float = 0.0
    trades_count: int = 0
    wins: int = 0
    losses: int = 0

    @property
    def pnl_pct(self) -> float:
        """Daily P/L as percentage of starting balance."""
        if self.starting_balance <= 0:
            return 0.0
        return (self.realized_pnl / self.starting_balance) * 100

    @property
    def win_rate(self) -> float:
        """Win rate as a float between 0 and 1."""
        if self.trades_count == 0:
            return 0.0
        return self.wins / self.trades_count

    def to_dict(self):
        """Convert to dictionary with date serialized."""
        data = asdict(self)
        data["date"] = self.date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        if isinstance(data.get("date"), str):
            data["date"] = date.fromisoformat(data["date"])
        return cls(**data)


@dataclass
class RiskCheck:
    """Result of a risk validation check."""

    approved: bool
    reason: str
    position_size: float = 0.0
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
