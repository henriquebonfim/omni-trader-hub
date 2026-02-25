import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from src.main import OmniTrader
from src.exchange import Position

@pytest.fixture
def bot():
    with patch("src.main.get_config") as mock_config:
        # Mock config
        mock_config.return_value.trading.symbol = "BTC/USDT"
        mock_config.return_value.strategy.name = "ema_volume"
        mock_config.return_value.exchange.paper_mode = True

        # Mock dependencies
        with patch("src.main.Exchange") as MockExchange, \
             patch("src.main.Database") as MockDatabase, \
             patch("src.main.RiskManager") as MockRisk, \
             patch("src.main.Notifier") as MockNotifier, \
             patch("src.main.get_strategy") as mock_get_strategy:

            # Setup strategy mock
            mock_strategy = MagicMock()
            mock_strategy.metadata = {}
            mock_get_strategy.return_value.return_value = mock_strategy

            bot = OmniTrader()
            yield bot

@pytest.mark.asyncio
async def test_close_position_slippage(bot):
    # Setup
    position = Position({
        "symbol": "BTC/USDT",
        "side": "long",
        "contracts": 1.0,
        "entryPrice": 50000.0,
        "notional": 50000.0,
        "unrealizedPnl": 0.0,
        "leverage": 1,
        "liquidationPrice": 0.0
    })

    current_price = 51000.0 # Expected price

    # Mock close_position to return an order with a different average price
    bot.exchange.close_position = AsyncMock(return_value={
        "average": 50900.0, # Actual fill price (worse than expected)
        "price": 50900.0,
        "filled": 1.0
    })

    bot.database.log_trade_close = AsyncMock()
    bot.risk.record_trade = MagicMock()
    bot.notifier.trade_closed = AsyncMock()
    bot.risk.check_circuit_breaker = MagicMock(return_value=False)
    bot.exchange.cancel_all_orders = AsyncMock()

    # Execute
    await bot._close_position(position, current_price, "test_reason")

    # Verify
    # Slippage for Long Exit: Expected (51000) - Actual (50900) = 100.0 (Positive = Bad)
    bot.database.log_trade_close.assert_called_once()
    call_args = bot.database.log_trade_close.call_args[1]

    assert call_args["expected_price"] == 51000.0
    assert call_args["slippage"] == 100.0
    assert call_args["price"] == 50900.0

@pytest.mark.asyncio
async def test_reconcile_positions_with_trades(bot):
    # Setup: DB says OPEN, Exchange says FLAT
    last_trade = {
        "id": 1,
        "action": "OPEN",
        "side": "LONG",
        "timestamp": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "price": 50000.0,
        "size": 1.0,
        "stop_loss": 49000.0
    }
    bot.database.get_last_trade = AsyncMock(return_value=last_trade)

    position = Position() # Flat position

    # Mock fetch_my_trades to return a closing trade
    closing_trade = {
        "timestamp": datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc).timestamp() * 1000,
        "side": "sell", # Closing side for LONG
        "amount": 1.0,
        "price": 50500.0
    }
    bot.exchange.fetch_my_trades = AsyncMock(return_value=[closing_trade])
    bot.database.log_trade_close = AsyncMock()
    bot.notifier.send = AsyncMock()
    bot.exchange.get_ticker = AsyncMock() # Should not be called if trade found
    bot.risk.record_trade = MagicMock()

    # Execute
    await bot._reconcile_positions("BTC/USDT", position)

    # Verify
    bot.exchange.fetch_my_trades.assert_called_once()

    bot.database.log_trade_close.assert_called_once()
    call_args = bot.database.log_trade_close.call_args[1]

    # Should use price from trade (50500.0), not ticker or SL
    assert call_args["price"] == 50500.0
    assert call_args["reason"] == "reconciliation_detected_close"

@pytest.mark.asyncio
async def test_reconcile_positions_fallback(bot):
    # Setup: DB says OPEN, Exchange says FLAT
    last_trade = {
        "id": 1,
        "action": "OPEN",
        "side": "LONG",
        "timestamp": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "price": 50000.0,
        "size": 1.0,
        "stop_loss": 49000.0
    }
    bot.database.get_last_trade = AsyncMock(return_value=last_trade)
    position = Position()

    # Mock fetch_my_trades returning NO relevant trades
    bot.exchange.fetch_my_trades = AsyncMock(return_value=[])

    # Mock ticker for fallback
    bot.exchange.get_ticker = AsyncMock(return_value={"last": 48000.0})

    bot.database.log_trade_close = AsyncMock()
    bot.notifier.send = AsyncMock()
    bot.risk.record_trade = MagicMock()

    # Execute
    await bot._reconcile_positions("BTC/USDT", position)

    # Verify
    bot.exchange.fetch_my_trades.assert_called_once()
    bot.exchange.get_ticker.assert_called_once()

    bot.database.log_trade_close.assert_called_once()
    call_args = bot.database.log_trade_close.call_args[1]

    # Current price (48000) < SL (49000), so should assume SL hit
    assert call_args["price"] == 49000.0
