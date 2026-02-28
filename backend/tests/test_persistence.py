import pytest
from unittest.mock import AsyncMock, patch
import json
import os
import sys

# Add backend to sys.path to ensure imports work correctly
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from src.database.redis_store import RedisStore
from src.risk import RiskManager
from datetime import date

@pytest.mark.asyncio
async def test_redis_store_connection():
    """Test Redis connection logic."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client

        # Ensure ping returns True (awaited)
        mock_client.ping.return_value = True

        store = RedisStore()
        await store.connect()

        mock_from_url.assert_called_once()
        mock_client.ping.assert_awaited_once()

        # Test close
        await store.close()
        mock_client.aclose.assert_awaited_once()

@pytest.mark.asyncio
async def test_redis_store_set_get():
    """Test setting and getting values."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client

        # Setup mock behavior
        # get should return a JSON string
        mock_client.get.return_value = json.dumps({"foo": "bar"})

        store = RedisStore()

        # Test Set
        await store.set("test_key", {"foo": "bar"})
        # We need to verify connect was called implicitly if not connected
        mock_from_url.assert_called()

        # Verify set called with JSON string
        mock_client.set.assert_awaited_with("test_key", '{"foo": "bar"}')

        # Test Get
        val = await store.get("test_key")
        assert val == {"foo": "bar"}
        mock_client.get.assert_awaited_with("test_key")

@pytest.mark.asyncio
async def test_risk_manager_state_persistence():
    """Test RiskManager saves and restores state."""

    # Mock RedisStore through Factory
    with patch("src.database.factory.DatabaseFactory.get_redis_store") as mock_get_store:
        mock_redis_instance = AsyncMock()
        mock_get_store.return_value = mock_redis_instance

        # 1. Initialize RiskManager
        risk = RiskManager()
        risk.daily_stats.starting_balance = 1000.0

        # 2. Simulate trading activity
        # record_trade calls save_state internally
        await risk.record_trade(100.0) # Win (+100)
        await risk.record_trade(-50.0) # Loss (-50)

        # Verify in-memory state
        assert risk.daily_stats.realized_pnl == 50.0
        assert risk.daily_stats.trades_count == 2
        assert risk.daily_stats.wins == 1
        assert risk.daily_stats.losses == 1
        assert risk.consecutive_losses == 1

        # Verify save_state was triggered
        assert mock_redis_instance.set.called

        # 3. Simulate Restart / Restore
        # Prepare data to be returned by redis.get
        # The key names will include prefix, we can just mock return values based on call args or order
        # But simpler to just mock the return values for specific calls if we can, or general side_effect.

        stored_stats = risk.daily_stats.to_dict()

        async def mock_get_side_effect(key):
            if "daily_stats" in key:
                return stored_stats
            if "consecutive_losses" in key:
                return 1 # Last state was 1 loss
            if "circuit_breaker" in key:
                return False
            if "weekly_circuit_breaker" in key:
                return False
            return None

        mock_redis_instance.get.side_effect = mock_get_side_effect

        # Create NEW risk manager instance to test load
        # Since we patched RedisStore class, new instance gets a NEW mock by default unless we control it.
        # But wait, patch returns the SAME Mock class, so calling it returns a NEW Mock instance.
        # We need to ensure the NEW instance uses a mock that returns our data.

        # Let's manually assign the mock to the new instance's redis attribute to be sure,
        # or configure the MockClass to return our configured instance.
        # Ensure all factory calls return the same mock instance
        mock_get_store.return_value = mock_redis_instance

        new_risk = RiskManager()
        await new_risk.load_state()

        # Verify state restored
        assert new_risk.daily_stats.realized_pnl == 50.0
        assert new_risk.daily_stats.trades_count == 2
        assert new_risk.consecutive_losses == 1
        assert new_risk.daily_stats.date == date.today()

@pytest.mark.asyncio
async def test_weekly_circuit_breaker_persistence():
    """Test Weekly Circuit Breaker state is persisted."""

    with patch("src.database.factory.DatabaseFactory.get_redis_store") as mock_get_store:
        mock_redis_instance = AsyncMock()
        mock_get_store.return_value = mock_redis_instance

        risk = RiskManager()
        risk.max_weekly_loss_pct = 10.0 # 10%

        # Trigger breaker
        # Current Balance = 1000. Weekly PnL = -150.
        # Start Balance = 1150. PnL % = -150/1150 = -13.04%
        # This calls save_state if changed
        triggered = await risk.check_weekly_circuit_breaker(-150.0, 1000.0)

        assert triggered is True
        assert risk._weekly_circuit_breaker_active is True

        # Verify persistence call
        assert mock_redis_instance.set.called

        # Verify correct key/value was set
        # We look for a call setting weekly_circuit_breaker to True
        # args[0] is key, args[1] is value
        calls = mock_redis_instance.set.await_args_list
        found = False
        for call in calls:
            args = call.args
            # Key contains "weekly_circuit_breaker" and value is True
            if "weekly_circuit_breaker" in args[0] and args[1] is True:
                found = True
                break
        assert found
