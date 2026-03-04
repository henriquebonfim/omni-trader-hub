from unittest.mock import AsyncMock, MagicMock

import pytest

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

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long.return_value = {"id": "1", "average": 50100.0}
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 50100.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
    }

    await bot._open_position("long", 50000.0, 1000.0)

    # Verify DB Log
    bot.database.log_trade_open.assert_called_once()
    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs["expected_price"] == 50000.0
    assert kwargs["slippage"] == 100.0


@pytest.mark.asyncio
async def test_slippage_favorable():
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()

    bot.config.trading.symbol = "BTC/USDT"
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    # Market Long - Favorable
    # Signal: 50000, Fill: 49900
    # Slippage: 49900 - 50000 = -100

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long.return_value = {"id": "2", "average": 49900.0}
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 49900.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
    }
    await bot._open_position("long", 50000.0, 1000.0)

    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs["slippage"] == -100.0


@pytest.mark.asyncio
async def test_slippage_zero():
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()

    bot.config.trading.symbol = "BTC/USDT"
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long.return_value = {"id": "3", "average": 50000.0}
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 50000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
    }
    await bot._open_position("long", 50000.0, 1000.0)

    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs["slippage"] == 0.0


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

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_short.return_value = {"id": "4", "average": 49900.0}
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 49900.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
    }

    await bot._open_position("short", 50000.0, 1000.0)

    # Verify DB Log
    bot.database.log_trade_open.assert_called_once()
    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs["expected_price"] == 50000.0
    assert kwargs["slippage"] == 100.0
