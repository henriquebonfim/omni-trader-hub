import structlog

from src.domain.shared.value_objects import Leverage, Percentage, Price, Side
from src.domain.trading.services import risk_validator

from .models import RiskCheck

logger = structlog.get_logger()


def _to_side(side: str) -> Side:
    if side == "long":
        return Side.LONG
    if side == "short":
        return Side.SHORT
    raise ValueError(f"Unsupported side: {side}")


class TradeValidator:
    """Validates trades against risk rules."""

    def __init__(self, config, sizer):
        self.config = config
        self.sizer = sizer

    def validate_trade(
        self,
        side: str,
        balance: float,
        entry_price: float,
        peak_equity: float,
        consecutive_losses: int,
        daily_breaker_active: bool,
        current_positions: int = 0,
        symbol: str = "BTC/USDT",
        exchange=None,
        ohlcv=None,
    ) -> RiskCheck:
        """Validate trade and return RiskCheck."""
        min_size = 0.001
        if exchange and symbol in exchange.markets:
            try:
                min_size = exchange.markets[symbol].get("limits", {}).get("amount", {}).get("min", 0.001)
            except (KeyError, AttributeError, TypeError):
                pass

        check = risk_validator.validate_trade(
            side=_to_side(side),
            balance=balance,
            entry_price=Price(entry_price),
            position_size_pct=Percentage(self.config.trading.position_size_pct),
            leverage=Leverage(self.config.exchange.leverage),
            peak_equity=peak_equity,
            auto_deleverage_threshold_pct=Percentage(
                self.config.risk.auto_deleverage_threshold_pct
                if hasattr(self.config.risk, "auto_deleverage_threshold_pct")
                else 10.0
            ),
            consecutive_losses=consecutive_losses,
            stop_loss_pct=Percentage(self.config.risk.stop_loss_pct),
            take_profit_pct=Percentage(self.config.risk.take_profit_pct),
            circuit_breaker_active=daily_breaker_active,
            max_positions=self.config.risk.max_positions,
            current_positions=current_positions,
            min_size=min_size,
        )

        if not check.approved:
            return RiskCheck(approved=False, reason=check.reason)

        if self.config.risk.use_atr_stops and ohlcv is not None:
            stop_loss, take_profit = self.sizer.calculate_atr_stops(entry_price, side, ohlcv)
            return RiskCheck(
                approved=True,
                reason=check.reason,
                position_size=float(check.position_size),
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
            )

        return RiskCheck(
            approved=True,
            reason=check.reason,
            position_size=float(check.position_size),
            stop_loss_price=float(check.stop_loss_price),
            take_profit_price=float(check.take_profit_price),
        )
