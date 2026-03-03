from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exchange import Position
from src.main import OmniTrader


@pytest.fixture
def bot():
    with patch("src.main.get_config") as mock_config:
        # Mock config
        mock_config.return_value.trading.symbol = "BTC/USDT"
        mock_config.return_value.strategy.name = "ema_volume"
        mock_config.return_value.exchange.paper_mode = True

        # Mock dependencies
        with patch("src.main.Exchange"), \
             patch("src.main.DatabaseFactory") as mock_db_factory, \
             patch("src.main.RiskManager"), \
             patch("src.main.Notifier") as MockNotifier, \
             patch("src.main.get_strategy") as mock_get_strategy:

            # Setup DB mock
            mock_db_factory.get_database.return_value = AsyncMock()

            # Setup strategy mock
            mock_strategy = MagicMock()
            mock_strategy.metadata = {}
            mock_get_strategy.return_value.return_value = mock_strategy

            # Mock Notifier as AsyncMock to support await calls
            MockNotifier.return_value = AsyncMock()

            bot = OmniTrader()
            yield bot

@pytest.mark.asyncio
async def test_open_position_sl_failure_flattens_position(bot):
    bot.config.trading.symbol = "BTC/USDT"
    
    # Mock validation to approve
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    
    # Mock exchange
    bot.exchange.market_long = AsyncMock(return_value={"id": "order123", "average": 50000.0})
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(return_value={
        "average_price": 50000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
        "confirmed": True
    })
    
    # Make set_stop_loss ALWAYS fail
    bot.exchange.set_stop_loss = AsyncMock(side_effect=Exception("API Error"))
    bot.exchange.set_take_profit = AsyncMock()
    
    # Mock _close_position and get_position
    bot._close_position = AsyncMock()
    open_pos = Position({"symbol": "BTC/USDT", "side": "long", "contracts": 1.0, "entryPrice": 50000.0})
    bot.exchange.get_position = AsyncMock(return_value=open_pos)
    
    # Patch asyncio.sleep to not actually sleep during tests
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")
    
    # Assertions
    assert bot.exchange.set_stop_loss.call_count == 4
    assert mock_sleep.call_count == 3  # Slept 3 times
    
    bot.exchange.set_take_profit.assert_not_called()
    bot._close_position.assert_called_once_with(open_pos, 50000.0, "emergency_close_sl_placement_failed")
    bot.database.log_trade_open.assert_not_called()

@pytest.mark.asyncio
async def test_open_position_tp_failure_flattens_position(bot):
    bot.config.trading.symbol = "BTC/USDT"
    
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    
    bot.exchange.market_long = AsyncMock(return_value={"id": "order123", "average": 50000.0})
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(return_value={
        "average_price": 50000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
        "confirmed": True
    })
    
    bot.exchange.set_stop_loss = AsyncMock()
    # Make set_take_profit ALWAYS fail
    bot.exchange.set_take_profit = AsyncMock(side_effect=Exception("API Error"))
    
    bot._close_position = AsyncMock()
    open_pos = Position({"symbol": "BTC/USDT", "side": "long", "contracts": 1.0, "entryPrice": 50000.0})
    bot.exchange.get_position = AsyncMock(return_value=open_pos)
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")
    
    assert bot.exchange.set_stop_loss.call_count == 1
    assert bot.exchange.set_take_profit.call_count == 4
    assert mock_sleep.call_count == 3
    
    bot._close_position.assert_called_once_with(open_pos, 50000.0, "emergency_close_tp_placement_failed")
    bot.database.log_trade_open.assert_not_called()

@pytest.mark.asyncio
async def test_open_position_success_with_retries(bot):
    bot.config.trading.symbol = "BTC/USDT"
    
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    
    bot.exchange.market_long = AsyncMock(return_value={"id": "order123", "average": 50000.0})
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(return_value={
        "average_price": 50000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
        "confirmed": True
    })
    
    # Fail twice, then succeed
    bot.exchange.set_stop_loss = AsyncMock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), None])
    bot.exchange.set_take_profit = AsyncMock(side_effect=[Exception("Fail 1"), None])
    
    bot._close_position = AsyncMock()
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")
    
    assert bot.exchange.set_stop_loss.call_count == 3
    assert bot.exchange.set_take_profit.call_count == 2
    assert mock_sleep.call_count == 3  # 2 for SL, 1 for TP
    
    bot._close_position.assert_not_called()
    bot.database.log_trade_open.assert_called_once()

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
        "id": "123",
        "average": 50900.0, # Actual fill price (worse than expected)
        "price": 50900.0,
        "filled": 1.0
    })

    bot.exchange.get_order_fill_details = AsyncMock(return_value={
        "average_price": 50900.0,
        "total_fee": 0.0,
        "fee_currency": "USDT",
        "timestamp": 1234567890
    })

    # Mock database fee query
    bot.database.get_open_trade_fee = AsyncMock(return_value=2.0)

    bot.database.log_trade_close = AsyncMock()
    bot.risk.record_trade = AsyncMock()
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
    bot.risk.record_trade = AsyncMock()

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
    bot.risk.record_trade = AsyncMock()

    # Execute
    await bot._reconcile_positions("BTC/USDT", position)

    # Verify
    bot.exchange.fetch_my_trades.assert_called_once()
    bot.exchange.get_ticker.assert_called_once()

    bot.database.log_trade_close.assert_called_once()
    call_args = bot.database.log_trade_close.call_args[1]

    # Current price (48000) < SL (49000), so should assume SL hit
    assert call_args["price"] == 49000.0
