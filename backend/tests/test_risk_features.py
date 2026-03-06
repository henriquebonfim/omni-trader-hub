from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from src.risk import RiskManager


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_weekly_circuit_breaker_triggered(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    # Setup
    risk = RiskManager()
    risk.max_weekly_loss_pct = 10.0

    current_balance = 9000.0
    weekly_pnl = -1100.0  # Started with ~10100. Loss > 10%

    # check_weekly_circuit_breaker(weekly_pnl, current_balance)
    triggered = await risk.check_weekly_circuit_breaker(weekly_pnl, current_balance)

    assert triggered is True
    assert risk._weekly_circuit_breaker_active is True


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_weekly_circuit_breaker_not_triggered(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    risk = RiskManager()
    risk.max_weekly_loss_pct = 10.0

    current_balance = 9500.0
    weekly_pnl = -500.0  # Started with 10000. Loss 5%

    triggered = await risk.check_weekly_circuit_breaker(weekly_pnl, current_balance)
    assert triggered is False


def test_black_swan_detector():
    risk = RiskManager()

    # Create OHLCV with extreme move
    now = pd.Timestamp.now()
    times = [now - timedelta(minutes=i) for i in range(60)]
    times.reverse()

    # Normal data then crash
    data = {
        "open": [50000.0] * 60,
        "high": [50000.0] * 60,
        "low": [50000.0] * 60,
        "close": [50000.0] * 60,
        "volume": [100.0] * 60,
    }

    df = pd.DataFrame(data, index=times)

    # Modify to have a huge drop
    # High 50k, Low 40k -> 10k drop -> 25% move (10k/40k) -> > 10%
    df.loc[df.index[-1], "low"] = 40000.0

    triggered = risk.check_black_swan(df)
    assert triggered is True


def test_black_swan_detector_normal():
    risk = RiskManager()

    now = pd.Timestamp.now()
    times = [now - timedelta(minutes=i) for i in range(60)]
    times.reverse()

    data = {
        "open": [49500.0] * 60,
        "high": [50000.0] * 60,
        "low": [49000.0] * 60,  # 2% range
        "close": [49500.0] * 60,
        "volume": [100.0] * 60,
    }
    df = pd.DataFrame(data, index=times)

    triggered = risk.check_black_swan(df)
    assert triggered is False


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_auto_deleverage_drawdown_across_days(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    risk = RiskManager()
    risk.auto_deleverage_threshold = 15.0  # 15% threshold
    risk.position_size_pct = 10.0  # Risk 10% of balance per trade
    risk.leverage = 5

    # Initial state
    initial_balance = 10000.0
    await risk.initialize_daily_stats(initial_balance)
    assert risk.peak_equity == 10000.0

    # Normal position sizing (No drawdown)
    # Risk amount = 10000 * 0.10 = 1000
    # Notional = 1000 * 5 (leverage) = 5000
    # Position size = 5000 / 50000 = 0.1
    size_normal = risk.calculate_position_size(10000.0, 50000.0)
    assert size_normal == pytest.approx(0.1)

    # Day 1: Lose 10% (Balance: 9000, Peak: 10000)
    # Drawdown = 10%. Threshold is 15%. No auto-deleverage yet.
    # Risk amount = 9000 * 0.10 = 900
    # Notional = 900 * 5 = 4500
    # Position size = 4500 / 50000 = 0.09
    size_day1 = risk.calculate_position_size(9000.0, 50000.0)
    assert size_day1 == pytest.approx(0.09)

    # Simulate Day 2 Reset
    # Peak equity should remain 10000.0
    risk.daily_stats.date = pd.Timestamp.now().date() - timedelta(days=1)
    await risk.initialize_daily_stats(9000.0)
    assert risk.peak_equity == 10000.0

    # Day 2: Lose another 10% from original peak (Balance: 8000, Peak: 10000)
    # Drawdown = 20%. Threshold is 15%. Auto-deleverage SHOULD trigger.
    # Leverage drops to 1.
    # Risk amount = 8000 * 0.10 = 800
    # Notional = 800 * 1 (leverage) = 800
    # Position size = 800 / 50000 = 0.016
    size_day2 = risk.calculate_position_size(8000.0, 50000.0)
    assert size_day2 == pytest.approx(0.016)

    # Recover slightly (Balance: 8600, Peak: 10000)
    # Drawdown = 14%. Auto-deleverage OFF.
    # Leverage returns to 5.
    # Risk amount = 8600 * 0.10 = 860
    # Notional = 860 * 5 = 4300
    # Position size = 4300 / 50000 = 0.086
    size_recovery = risk.calculate_position_size(8600.0, 50000.0)
    assert size_recovery == pytest.approx(0.086)

    # Reach new all-time high (Balance: 12000)
    await risk.initialize_daily_stats(12000.0)
    assert risk.peak_equity == 12000.0

    # Drawdown resets against new peak
    size_ath = risk.calculate_position_size(12000.0, 50000.0)
    # Risk amount = 12000 * 0.10 = 1200
    # Notional = 1200 * 5 = 6000
    # Size = 6000 / 50000 = 0.12
    assert size_ath == pytest.approx(0.12)


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_consecutive_losses_carry_across_days(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    risk = RiskManager()
    risk.position_size_pct = 10.0
    risk.leverage = 1

    # Initial state Day 1
    await risk.initialize_daily_stats(10000.0)

    # 2 losses on Day 1
    await risk.record_trade(-100.0)
    await risk.record_trade(-100.0)

    assert risk.consecutive_losses == 2

    # Simulate Day 2 Reset
    risk.daily_stats.date = pd.Timestamp.now().date() - timedelta(days=1)
    await risk.initialize_daily_stats(9800.0)

    # Consecutive losses should NOT reset
    assert risk.consecutive_losses == 2

    # 1 more loss on Day 2 -> total 3 consecutive losses
    await risk.record_trade(-100.0)
    assert risk.consecutive_losses == 3

    # Position size should be reduced by 50%
    # Balance: 9700. Risk amount = 9700 * 0.10 = 970
    # Expected size before reduction: 970 / 50000 = 0.0194
    # Expected size after 50% reduction: 0.0097
    size_reduced = risk.calculate_position_size(9700.0, 50000.0)
    assert size_reduced == pytest.approx(0.0097)

    # Record a win on Day 2
    await risk.record_trade(200.0)

    # Consecutive losses should reset on win
    assert risk.consecutive_losses == 0

    # Position size should be normal
    # Balance: 9900. Risk amount = 9900 * 0.10 = 990
    # Expected size: 990 / 50000 = 0.0198
    size_normal = risk.calculate_position_size(9900.0, 50000.0)
    assert size_normal == pytest.approx(0.0198)
