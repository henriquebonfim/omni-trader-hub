import datetime
import pytest
from unittest.mock import AsyncMock, patch
from src.risk import RiskManager


def test_drawdown_sizing():
    risk = RiskManager()
    risk.consecutive_losses = 3
    risk.position_size_pct = 2.0
    risk.leverage = 1.0

    # Normal size: 10000 * 0.02 = 200
    # Halved: 100

    size = risk.calculate_position_size(10000.0, 1.0)
    assert size == 100.0

@pytest.mark.asyncio
async def test_consecutive_losses_reset():
    with patch("src.database.factory.DatabaseFactory.get_redis_store") as mock_get_store:
        mock_get_store.return_value = AsyncMock()

        risk = RiskManager()
        risk.consecutive_losses = 5

        # Simulate trade win
        await risk.record_trade(100.0)
        assert risk.consecutive_losses == 0

        # Simulate trade loss
        await risk.record_trade(-100.0)
        assert risk.consecutive_losses == 1

@pytest.mark.asyncio
async def test_daily_reset_clears_streak(monkeypatch):
    with patch("src.database.factory.DatabaseFactory.get_redis_store") as mock_get_store:
        mock_get_store.return_value = AsyncMock()

        risk = RiskManager()
        risk.consecutive_losses = 3

        # Trigger new day reset
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        class MockDate(datetime.date):
            @classmethod
            def today(cls):
                return tomorrow

            # Allow creating date objects from date(Y, M, D) calls inside RiskManager if needed
            # But RiskManager uses date.today() which we patched on the class.
            # However, datetime.date is immutable type, so we need care.
            # But the monkeypatch below targets src.risk.date which is imported as 'date'.

        monkeypatch.setattr("src.risk.date", MockDate)
        await risk.initialize_daily_stats(10000.0)

        assert risk.consecutive_losses == 0
