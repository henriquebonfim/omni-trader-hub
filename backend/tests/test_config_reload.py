import pytest
from unittest.mock import MagicMock, AsyncMock
from src.main import OmniTrader

@pytest.mark.asyncio
async def test_reload_config_updates_components(monkeypatch):
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.strategy = MagicMock()
    bot.notifier = MagicMock()

    # Mock reload_config to return a new config object
    new_config = MagicMock()
    new_config.strategy.name = "ema_volume" # Same name to avoid class switch

    monkeypatch.setattr("src.main.reload_config", lambda: new_config)

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

    # Mock get_strategy
    NewStrategyClass = MagicMock()
    # Ensure instantiation returns a unique mock
    NewStrategyInstance = MagicMock()
    NewStrategyClass.return_value = NewStrategyInstance

    monkeypatch.setattr("src.main.reload_config", lambda: new_config)
    monkeypatch.setattr("src.main.get_strategy", lambda name: NewStrategyClass)

    await bot.reload_config()

    # Verify strategy re-instantiated
    NewStrategyClass.assert_called_once_with(new_config)
    assert bot.strategy is NewStrategyInstance
