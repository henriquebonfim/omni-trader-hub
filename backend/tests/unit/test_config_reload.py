from unittest.mock import AsyncMock, MagicMock

import pytest

from src.main import OmniTrader


@pytest.mark.asyncio
async def test_reload_config_updates_components(monkeypatch):
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.strategy = MagicMock()
    bot.notifier = MagicMock()

    # Mock load_config_from_db to return a new config object
    async def mock_load_from_db(db):
        return new_config

    monkeypatch.setattr("src.main.load_config_from_db", mock_load_from_db)

    await bot.reload_config()

    # Verify components updated
    bot.exchange.update_config.assert_called_once_with(new_config)
    bot.risk.update_config.assert_called_once_with(new_config)
    bot.strategy.update_config.assert_called_once_with(new_config)
    bot.notifier.update_config.assert_called_once_with(new_config)


@pytest.mark.asyncio
async def test_reload_config_switches_strategy(monkeypatch):
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.notifier = MagicMock()

    # Initial strategy
    bot.config.strategy.name = "ema_volume"
    bot.strategy = MagicMock()

    # New config with different strategy
    new_config = MagicMock()
    new_config.strategy.name = "adx_trend"

    # Mock load_config_from_db
    async def mock_load_from_db(db):
        return new_config

    # Mock get_strategy
    NewStrategyClass = MagicMock()
    # Ensure instantiation returns a unique mock
    NewStrategyInstance = MagicMock()
    NewStrategyClass.return_value = NewStrategyInstance

    monkeypatch.setattr("src.main.load_config_from_db", mock_load_from_db)
    monkeypatch.setattr("src.main.get_strategy", lambda name: NewStrategyClass)

    await bot.reload_config()

    # Verify strategy re-instantiated
    NewStrategyClass.assert_called_once_with(new_config)
    assert bot.strategy is NewStrategyInstance
