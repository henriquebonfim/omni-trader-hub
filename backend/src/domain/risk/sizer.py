import pandas as pd
import structlog

from src.domain import indicators
from src.domain.shared.value_objects import Leverage, Percentage, Price, Side
from src.domain.trading.services import risk_validator

logger = structlog.get_logger()


def _to_side(side: str) -> Side:
    if side == "long":
        return Side.LONG
    if side == "short":
        return Side.SHORT
    raise ValueError(f"Unsupported side: {side}")


class PositionSizer:
    """Handles position sizing, SL/TP, and trailing stop calculations."""

    def __init__(self, config):
        self.config = config

    def calculate_position_size(
        self, balance: float, entry_price: float, peak_equity: float, consecutive_losses: int
    ) -> float:
        """Calculate position size based on risk parameters."""
        size = risk_validator.calculate_position_size(
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
        )
        return float(size)

    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate fixed percentage stop loss."""
        return float(
            risk_validator.calculate_stop_loss(
                entry_price=Price(entry_price),
                side=_to_side(side),
                stop_loss_pct=Percentage(self.config.risk.stop_loss_pct),
            )
        )

    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate fixed percentage take profit."""
        return float(
            risk_validator.calculate_take_profit(
                entry_price=Price(entry_price),
                side=_to_side(side),
                take_profit_pct=Percentage(self.config.risk.take_profit_pct),
            )
        )

    def calculate_atr_stops(
        self, entry_price: float, side: str, ohlcv: pd.DataFrame
    ) -> tuple[float, float]:
        """Calculate SL/TP using ATR."""
        if ohlcv is None or ohlcv.empty:
            return (
                self.calculate_stop_loss(entry_price, side),
                self.calculate_take_profit(entry_price, side),
            )

        try:
            atr = indicators.atr(
                ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.config.risk.atr_period
            )
            if atr is None or atr.empty:
                return (
                    self.calculate_stop_loss(entry_price, side),
                    self.calculate_take_profit(entry_price, side),
                )

            current_atr = atr.iloc[-1]
            if pd.isna(current_atr) or current_atr <= 0:
                # Fallback ATR calculation (Manual TR average)
                prev_close = ohlcv["close"].shift(1).bfill()
                tr = pd.concat(
                    [
                        ohlcv["high"] - ohlcv["low"],
                        (ohlcv["high"] - prev_close).abs(),
                        (ohlcv["low"] - prev_close).abs(),
                    ],
                    axis=1,
                ).max(axis=1)
                fallback_atr = tr.rolling(window=self.config.risk.atr_period, min_periods=1).mean().iloc[-1]
                if pd.notna(fallback_atr) and fallback_atr > 0:
                    current_atr = float(fallback_atr)

            if pd.isna(current_atr) or current_atr <= 0:
                return (
                    self.calculate_stop_loss(entry_price, side),
                    self.calculate_take_profit(entry_price, side),
                )

            if side == "long":
                stop_loss = entry_price - (current_atr * self.config.risk.atr_multiplier_sl)
                take_profit = entry_price + (current_atr * self.config.risk.atr_multiplier_tp)
            else:  # short
                stop_loss = entry_price + (current_atr * self.config.risk.atr_multiplier_sl)
                take_profit = entry_price - (current_atr * self.config.risk.atr_multiplier_tp)

            return stop_loss, take_profit

        except Exception as e:
            logger.error("atr_stops_calculation_failed", error=str(e))
            return (
                self.calculate_stop_loss(entry_price, side),
                self.calculate_take_profit(entry_price, side),
            )

    def calculate_trailing_stop(self, current_price: float, position) -> float | None:
        """Calculate potential new stop loss price for trailing stop."""
        if not position.is_open:
            return None

        if position.side == "long":
            pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            if pnl_pct >= self.config.risk.trailing_stop_activation_pct:
                return current_price * (1 - self.config.risk.trailing_stop_callback_pct / 100)
        else:  # short
            pnl_pct = ((position.entry_price - current_price) / position.entry_price) * 100
            if pnl_pct >= self.config.risk.trailing_stop_activation_pct:
                return current_price * (1 + self.config.risk.trailing_stop_callback_pct / 100)

        return None
