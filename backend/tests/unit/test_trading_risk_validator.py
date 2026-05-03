from __future__ import annotations

import pandas as pd

from src.domain.shared.value_objects import Leverage, Percentage, Price, Side
from src.domain.trading.services.risk_validator import (
    calculate_position_size,
    detect_black_swan,
    validate_trade,
)


def test_calculate_position_size_applies_drawdown_and_loss_scaling() -> None:
    size = calculate_position_size(
        balance=1000.0,
        entry_price=Price(100.0),
        position_size_pct=Percentage(2.0),
        leverage=Leverage(10.0),
        peak_equity=1200.0,
        auto_deleverage_threshold_pct=Percentage(10.0),
        consecutive_losses=3,
    )

    # Drawdown threshold breached => leverage forced to 1
    # risk_amount=20, notional=20, size=0.2, consecutive losses>=3 => size=0.1
    assert float(size) == 0.1


def test_validate_trade_rejects_when_circuit_breaker_active() -> None:
    result = validate_trade(
        side=Side.LONG,
        balance=1000.0,
        entry_price=Price(100.0),
        position_size_pct=Percentage(2.0),
        leverage=Leverage(3.0),
        peak_equity=1000.0,
        auto_deleverage_threshold_pct=Percentage(10.0),
        consecutive_losses=0,
        stop_loss_pct=Percentage(2.0),
        take_profit_pct=Percentage(4.0),
        circuit_breaker_active=True,
        max_positions=1,
        current_positions=0,
    )

    assert result.approved is False
    assert "Circuit breaker" in result.reason


def test_validate_trade_returns_size_and_levels_on_success() -> None:
    result = validate_trade(
        side=Side.LONG,
        balance=1000.0,
        entry_price=Price(100.0),
        position_size_pct=Percentage(2.0),
        leverage=Leverage(3.0),
        peak_equity=1000.0,
        auto_deleverage_threshold_pct=Percentage(10.0),
        consecutive_losses=0,
        stop_loss_pct=Percentage(2.0),
        take_profit_pct=Percentage(4.0),
        circuit_breaker_active=False,
        max_positions=1,
        current_positions=0,
    )

    assert result.approved is True
    assert result.position_size is not None
    assert result.stop_loss_price is not None
    assert result.take_profit_price is not None


def test_detect_black_swan_true_on_large_move() -> None:
    idx = pd.date_range("2026-03-09 10:00:00", periods=5, freq="15min")
    ohlcv = pd.DataFrame(
        {
            "high": [100, 101, 110, 111, 112],
            "low": [99, 98, 97, 96, 95],
            "close": [100, 100, 108, 110, 111],
        },
        index=idx,
    )

    assert detect_black_swan(ohlcv, threshold_pct=0.10) is True


def test_detect_black_swan_false_on_small_move() -> None:
    idx = pd.date_range("2026-03-09 10:00:00", periods=5, freq="15min")
    ohlcv = pd.DataFrame(
        {
            "high": [100, 101, 101, 102, 102],
            "low": [99.5, 99.6, 99.7, 99.8, 99.9],
            "close": [100, 100.5, 100.7, 101, 101.2],
        },
        index=idx,
    )

    assert detect_black_swan(ohlcv, threshold_pct=0.10) is False
