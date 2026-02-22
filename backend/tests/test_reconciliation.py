from unittest.mock import AsyncMock, MagicMock

import pytest

from src.main import OmniTrader


@pytest.mark.asyncio
async def test_reconcile_positions_db_open_exchange_flat():
    bot = OmniTrader()
    bot.database = AsyncMock()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.notifier = AsyncMock()

    # DB says OPEN
    bot.database.get_last_trade.return_value = {
        "id": 1,
        "action": "OPEN",
        "side": "LONG",
        "price": "50000.0",
        "size": "0.1"
    }

    # Exchange says FLAT
    position = MagicMock()
    position.is_open = False

    bot.exchange.get_ticker.return_value = {"last": 51000.0}

    await bot._reconcile_positions("BTC/USDT", position)

    # Should log close
    bot.database.log_trade_close.assert_called_once()
    assert bot.database.log_trade_close.call_args[1]['reason'] == "reconciliation_detected_close"

@pytest.mark.asyncio
async def test_reconcile_positions_db_close_exchange_open():
    bot = OmniTrader()
    bot.database = AsyncMock()
    bot.exchange = AsyncMock()
    bot.risk = MagicMock()
    bot.notifier = AsyncMock()

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

    await bot._reconcile_positions("BTC/USDT", position)

    # Should log open
    bot.database.log_trade_open.assert_called_once()
    assert bot.database.log_trade_open.call_args[1]['reason'] == "reconciliation_detected_open"
