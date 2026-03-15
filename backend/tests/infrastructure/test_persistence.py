import os
import sys
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from src.risk import RiskManager


@pytest.mark.asyncio
async def test_risk_manager_state_persistence():
    """RiskManager saves and restores state through database state API."""
    with patch("src.database.factory.DatabaseFactory.get_database") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        risk = RiskManager()
        risk.daily_stats.starting_balance = 1000.0

        await risk.record_trade(100.0)
        await risk.record_trade(-50.0)

        assert risk.daily_stats.realized_pnl == 50.0
        assert risk.daily_stats.trades_count == 2
        assert risk.daily_stats.wins == 1
        assert risk.daily_stats.losses == 1
        assert risk.consecutive_losses == 1
        assert mock_db.set_state.called

        stored_stats = risk.daily_stats.to_dict()

        async def mock_get_state(key):
            if key.endswith("daily_stats"):
                return stored_stats
            if key.endswith("consecutive_losses"):
                return {"value": 1}
            if key.endswith("peak_equity"):
                return {"value": 0.0}
            if key.endswith("circuit_breaker"):
                return {"value": False}
            if key.endswith("weekly_circuit_breaker"):
                return {"value": False}
            return None

        mock_db.get_state.side_effect = mock_get_state

        new_risk = RiskManager()
        await new_risk.load_state()

        assert new_risk.daily_stats.realized_pnl == 50.0
        assert new_risk.daily_stats.trades_count == 2
        assert new_risk.consecutive_losses == 1
        assert new_risk.daily_stats.date == date.today()


@pytest.mark.asyncio
async def test_risk_manager_state_persistence_critical_failure():
    """RiskManager load_state/save_state fail fast when database persistence fails."""
    with patch("src.database.factory.DatabaseFactory.get_database") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.get_state.side_effect = Exception("Database down")
        mock_db.set_state.side_effect = Exception("Database down")

        risk = RiskManager()

        with pytest.raises(Exception, match="Database down"):
            await risk.load_state()

        with pytest.raises(Exception, match="Database down"):
            await risk.save_state()


@pytest.mark.asyncio
async def test_weekly_circuit_breaker_persistence():
    """Weekly circuit breaker state is persisted via database state API."""
    with patch("src.database.factory.DatabaseFactory.get_database") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        risk = RiskManager()
        risk.max_weekly_loss_pct = 10.0

        triggered = await risk.check_weekly_circuit_breaker(-150.0, 1000.0)

        assert triggered is True
        assert risk._weekly_circuit_breaker_active is True
        assert mock_db.set_state.called

        calls = mock_db.set_state.await_args_list
        found = False
        for call in calls:
            args = call.args
            if "weekly_circuit_breaker" in args[0] and args[1].get("value") is True:
                found = True
                break
        assert found
