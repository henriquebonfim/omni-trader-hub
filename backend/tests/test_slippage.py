import pytest
from unittest.mock import MagicMock, AsyncMock
from src.main import OmniTrader

@pytest.mark.asyncio
async def test_slippage_calculation_long():
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()

    # Setup
    bot.config.trading.symbol = "BTC/USDT"
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    # Market Long
    # Signal Price: 50000
    # Fill Price: 50100
    # Slippage: 50100 - 50000 = 100 (Unfavorable)

    bot.exchange.market_long.return_value = {"average": 50100.0}

    await bot._open_position("long", 50000.0, 1000.0)

    # Verify DB Log
    bot.database.log_trade_open.assert_called_once()
    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs['expected_price'] == 50000.0
    assert kwargs['slippage'] == 100.0

@pytest.mark.asyncio
async def test_slippage_calculation_short():
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()

    # Setup
    bot.config.trading.symbol = "BTC/USDT"
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    # Market Short
    # Signal Price: 50000
    # Fill Price: 49900
    # Slippage: 50000 - 49900 = 100 (Unfavorable)

    bot.exchange.market_short.return_value = {"average": 49900.0}

    await bot._open_position("short", 50000.0, 1000.0)

    # Verify DB Log
    bot.database.log_trade_open.assert_called_once()
    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs['expected_price'] == 50000.0
    assert kwargs['slippage'] == 100.0
