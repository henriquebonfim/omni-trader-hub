from datetime import timedelta

import pandas as pd

from src.risk import RiskManager


def test_weekly_circuit_breaker_triggered():
    # Setup
    risk = RiskManager()
    risk.max_weekly_loss_pct = 10.0

    current_balance = 9000.0
    weekly_pnl = -1100.0 # Started with ~10100. Loss > 10%

    # check_weekly_circuit_breaker(weekly_pnl, current_balance)
    triggered = risk.check_weekly_circuit_breaker(weekly_pnl, current_balance)

    assert triggered is True
    assert risk._weekly_circuit_breaker_active is True

def test_weekly_circuit_breaker_not_triggered():
    risk = RiskManager()
    risk.max_weekly_loss_pct = 10.0

    current_balance = 9500.0
    weekly_pnl = -500.0 # Started with 10000. Loss 5%

    triggered = risk.check_weekly_circuit_breaker(weekly_pnl, current_balance)
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
        "volume": [100.0] * 60
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
        "low": [49000.0] * 60, # 2% range
        "close": [49500.0] * 60,
        "volume": [100.0] * 60
    }
    df = pd.DataFrame(data, index=times)

    triggered = risk.check_black_swan(df)
    assert triggered is False
