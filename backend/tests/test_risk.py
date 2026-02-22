import pytest
from src.risk import RiskManager, DailyStats
import datetime

def test_drawdown_sizing():
    risk = RiskManager()
    risk.consecutive_losses = 3
    risk.position_size_pct = 2.0
    risk.leverage = 1.0

    # Normal size: 10000 * 0.02 = 200
    # Halved: 100

    size = risk.calculate_position_size(10000.0, 1.0)
    assert size == 100.0

def test_consecutive_losses_reset():
    risk = RiskManager()
    risk.consecutive_losses = 5

    # Simulate trade win
    risk.record_trade(100.0)
    assert risk.consecutive_losses == 0

    # Simulate trade loss
    risk.record_trade(-100.0)
    assert risk.consecutive_losses == 1

def test_daily_reset_clears_streak(monkeypatch):
    risk = RiskManager()
    risk.consecutive_losses = 3

    # Trigger new day reset
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    class MockDate(datetime.date):
        @classmethod
        def today(cls):
            return tomorrow

    monkeypatch.setattr("src.risk.date", MockDate)
    risk.initialize_daily_stats(10000.0)

    assert risk.consecutive_losses == 0
