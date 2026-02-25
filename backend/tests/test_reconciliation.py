from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest

from src.main import OmniTrader


@pytest.mark.asyncio
async def test_reconcile_positions_db_open_exchange_flat():
    bot = OmniTrader()
    bot.database = AsyncMock()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.risk.reconciliation_lookback_trades = 50

    # DB says OPEN
    ts_str = "2023-01-01T12:00:00"
    bot.database.get_last_trade.return_value = {
        "id": 1,
        "action": "OPEN",
        "side": "LONG",
        "price": "50000.0",
        "size": "0.1",
        "timestamp": ts_str
    }

    # Exchange says FLAT
    position = MagicMock()
    position.is_open = False

    # Calculate expected 'since' timestamp
    dt = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
    expected_since = int(dt.timestamp() * 1000)

    # Mock fetch_my_trades to find the closing trade
    # DB side LONG -> close side SELL
    bot.exchange.fetch_my_trades.return_value = [
        {
            "id": "101",
            "symbol": "BTC/USDT",
            "side": "sell",
            "price": 51500.0,
            "amount": 0.1,
            "timestamp": expected_since + 60000 # 1 minute later
        }
    ]

    await bot._reconcile_positions("BTC/USDT", position)

    # Should log close with FOUND price
    bot.database.log_trade_close.assert_called_once()
    kwargs = bot.database.log_trade_close.call_args[1]
    assert kwargs['reason'] == "reconciliation_detected_close"
    assert kwargs['price'] == 51500.0

    # Verify call with correct 'since' parameter
    bot.exchange.fetch_my_trades.assert_called_with("BTC/USDT", since=expected_since, limit=50)

@pytest.mark.asyncio
async def test_reconcile_positions_db_close_exchange_open():
    bot = OmniTrader()
    bot.database = AsyncMock()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.risk.reconciliation_lookback_trades = 50

    # DB says CLOSE
    bot.database.get_last_trade.return_value = {
        "id": 1,
        "action": "CLOSE",
    }

    # Exchange says OPEN
    position = MagicMock()
    position.is_open = True
    position.side = "long"
    position.entry_price = 50000.0
    position.size = 0.1
    position.notional = 5000.0

    # Mock fetch_my_trades to find the opening trade
    # Position side LONG -> open side BUY
    bot.exchange.fetch_my_trades.return_value = [
        {
            "id": "202",
            "symbol": "BTC/USDT",
            "side": "buy",
            "price": 49800.0, # Actual entry price different from position average (maybe fees/slippage)
            "amount": 0.1,
            "timestamp": 1672574460000
        }
    ]

    await bot._reconcile_positions("BTC/USDT", position)

    # Should log open with FOUND price
    bot.database.log_trade_open.assert_called_once()
    kwargs = bot.database.log_trade_open.call_args[1]
    assert kwargs['reason'] == "reconciliation_detected_open"
    assert kwargs['price'] == 49800.0
