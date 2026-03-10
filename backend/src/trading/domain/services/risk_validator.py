from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.shared.domain.value_objects import Leverage, Percentage, Price, Side, Size


@dataclass(frozen=True)
class RiskCheck:
    """Outcome of a risk validation check."""

    approved: bool
    reason: str
    position_size: Size | None = None
    stop_loss_price: Price | None = None
    take_profit_price: Price | None = None


def calculate_position_size(
    *,
    balance: float,
    entry_price: Price,
    position_size_pct: Percentage,
    leverage: Leverage,
    peak_equity: float,
    auto_deleverage_threshold_pct: Percentage,
    consecutive_losses: int,
) -> Size:
    """Calculate position size using risk %, leverage, and drawdown controls."""
    if balance <= 0:
        raise ValueError("Balance must be greater than 0")

    effective_leverage = float(leverage)
    if peak_equity > 0:
        drawdown_pct = ((peak_equity - balance) / peak_equity) * 100
        if drawdown_pct >= float(auto_deleverage_threshold_pct):
            effective_leverage = 1.0

    risk_amount = balance * (float(position_size_pct) / 100.0)
    notional_value = risk_amount * effective_leverage
    size = notional_value / float(entry_price)

    if consecutive_losses >= 3:
        size *= 0.5

    return Size(size)


def calculate_stop_loss(
    *, entry_price: Price, side: Side, stop_loss_pct: Percentage
) -> Price:
    if side == Side.LONG:
        return Price(float(entry_price) * (1.0 - float(stop_loss_pct) / 100.0))
    return Price(float(entry_price) * (1.0 + float(stop_loss_pct) / 100.0))


def calculate_take_profit(
    *, entry_price: Price, side: Side, take_profit_pct: Percentage
) -> Price:
    if side == Side.LONG:
        return Price(float(entry_price) * (1.0 + float(take_profit_pct) / 100.0))
    return Price(float(entry_price) * (1.0 - float(take_profit_pct) / 100.0))


def calculate_atr_stops(
    *,
    entry_price: Price,
    side: Side,
    current_atr: float,
    atr_multiplier_sl: float,
    atr_multiplier_tp: float,
) -> tuple[Price, Price]:
    if current_atr <= 0:
        raise ValueError("ATR must be greater than 0")

    if side == Side.LONG:
        stop_loss = float(entry_price) - (current_atr * atr_multiplier_sl)
        take_profit = float(entry_price) + (current_atr * atr_multiplier_tp)
    else:
        stop_loss = float(entry_price) + (current_atr * atr_multiplier_sl)
        take_profit = float(entry_price) - (current_atr * atr_multiplier_tp)

    return Price(stop_loss), Price(take_profit)


def detect_black_swan(ohlcv: pd.DataFrame, threshold_pct: float = 0.10) -> bool:
    """Detect extreme volatility in the last hour using high/low range."""
    if ohlcv is None or ohlcv.empty:
        return False

    last_timestamp = ohlcv.index[-1]
    one_hour_ago = last_timestamp - pd.Timedelta(hours=1)
    recent_data = ohlcv[ohlcv.index >= one_hour_ago]
    if recent_data.empty:
        return False

    high_max = recent_data["high"].max()
    low_min = recent_data["low"].min()
    if low_min <= 0:
        return False

    volatility_pct = (high_max - low_min) / low_min
    return bool(volatility_pct > threshold_pct)


def check_liquidation_risk(
    *,
    side: Side,
    entry_price: Price,
    liquidation_price: Price,
    current_price: Price,
    liquidation_buffer_pct: Percentage,
) -> bool:
    """Return True when remaining distance to liquidation is critically low."""
    _ = side  # Reserved for side-specific extensions.

    dist_to_liq = abs(float(current_price) - float(liquidation_price))
    total_dist = abs(float(entry_price) - float(liquidation_price))
    if total_dist == 0:
        return False

    remaining_pct = dist_to_liq / total_dist
    return remaining_pct < (float(liquidation_buffer_pct) / 100.0)


def validate_trade(
    *,
    side: Side,
    balance: float,
    entry_price: Price,
    position_size_pct: Percentage,
    leverage: Leverage,
    peak_equity: float,
    auto_deleverage_threshold_pct: Percentage,
    consecutive_losses: int,
    stop_loss_pct: Percentage,
    take_profit_pct: Percentage,
    circuit_breaker_active: bool,
    max_positions: int,
    current_positions: int,
    min_balance: float = 10.0,
    min_size: float = 0.001,
) -> RiskCheck:
    """Validate risk gates and return all required order sizing/SL/TP values."""
    if circuit_breaker_active:
        return RiskCheck(approved=False, reason="Circuit breaker active")

    if current_positions >= max_positions:
        return RiskCheck(approved=False, reason="Max positions reached")

    if balance < min_balance:
        return RiskCheck(
            approved=False,
            reason=f"Insufficient balance: ${balance:.2f} < ${min_balance}",
        )

    position_size = calculate_position_size(
        balance=balance,
        entry_price=entry_price,
        position_size_pct=position_size_pct,
        leverage=leverage,
        peak_equity=peak_equity,
        auto_deleverage_threshold_pct=auto_deleverage_threshold_pct,
        consecutive_losses=consecutive_losses,
    )

    if float(position_size) < min_size:
        return RiskCheck(
            approved=False,
            reason=f"Position too small: {float(position_size):.6f} < {min_size}",
        )

    stop_loss = calculate_stop_loss(
        entry_price=entry_price,
        side=side,
        stop_loss_pct=stop_loss_pct,
    )
    take_profit = calculate_take_profit(
        entry_price=entry_price,
        side=side,
        take_profit_pct=take_profit_pct,
    )

    return RiskCheck(
        approved=True,
        reason="Trade approved",
        position_size=position_size,
        stop_loss_price=stop_loss,
        take_profit_price=take_profit,
    )
