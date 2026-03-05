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
        with (
            patch("src.main.Exchange"),
            patch("src.main.DatabaseFactory") as mock_db_factory,
            patch("src.main.RiskManager"),
            patch("src.main.Notifier") as MockNotifier,
            patch("src.main.get_strategy") as mock_get_strategy,
        ):
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
async def test_max_positions_blocking(bot):
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.risk.max_positions = 1

    # Mock one open position existing
    existing_pos = Position(
        {"symbol": "ETH/USDT", "side": "long", "contracts": 1.0, "entryPrice": 3000.0}
    )
    bot.exchange.get_open_positions = AsyncMock(return_value=[existing_pos])

    # The risk manager uses max_positions = 1 (from config)
    # Re-init risk manager to pick up mock config
    from src.risk import RiskManager

    bot.risk = RiskManager()

    bot.exchange.market_long = AsyncMock()

    # Attempt to open position
    await bot._open_position("long", 50000.0, 10000.0, "test_reason")

    # Verify the order was NOT placed because max_positions is reached
    bot.exchange.market_long.assert_not_called()


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_redis_store")
async def test_max_positions_allowing(mock_get_store, bot):
    mock_get_store.return_value = AsyncMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.risk.max_positions = 2
    bot.config.trading.position_size_pct = 10.0
    bot.config.risk.stop_loss_pct = 1.0
    bot.config.risk.take_profit_pct = 2.0

    # Mock one open position existing
    existing_pos = Position(
        {"symbol": "ETH/USDT", "side": "long", "contracts": 1.0, "entryPrice": 3000.0}
    )
    bot.exchange.get_open_positions = AsyncMock(return_value=[existing_pos])

    # Mock exchange calls needed for a successful order
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )
    bot.exchange.set_stop_loss = AsyncMock()
    bot.exchange.set_take_profit = AsyncMock()
    bot.database.log_trade_open = AsyncMock()

    # Re-init risk manager to pick up mock config
    from src.risk import RiskManager

    bot.risk = RiskManager()

    # The risk manager needs daily_stats
    await bot.risk.initialize_daily_stats(10000.0)

    # Attempt to open position
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")

    # Verify the order WAS placed because 1 < 2
    bot.exchange.market_long.assert_called_once()


@pytest.mark.asyncio
async def test_open_position_sl_failure_flattens_position(bot):
    bot.config.trading.symbol = "BTC/USDT"

    # Mock validation to approve
    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    # Mock exchange
    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )

    # Make set_stop_loss ALWAYS fail
    bot.exchange.set_stop_loss = AsyncMock(side_effect=Exception("API Error"))
    bot.exchange.set_take_profit = AsyncMock()

    # Mock _close_position and get_position
    bot._close_position = AsyncMock()
    open_pos = Position(
        {"symbol": "BTC/USDT", "side": "long", "contracts": 1.0, "entryPrice": 50000.0}
    )
    bot.exchange.get_position = AsyncMock(return_value=open_pos)

    # Patch asyncio.sleep to not actually sleep during tests
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")

    # Assertions
    assert bot.exchange.set_stop_loss.call_count == 4
    assert mock_sleep.call_count == 3  # Slept 3 times

    bot.exchange.set_take_profit.assert_not_called()
    bot._close_position.assert_called_once_with(
        open_pos, 50000.0, "emergency_close_sl_placement_failed"
    )
    bot.database.log_trade_open.assert_not_called()


@pytest.mark.asyncio
async def test_open_position_tp_failure_flattens_position(bot):
    bot.config.trading.symbol = "BTC/USDT"

    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )

    bot.exchange.set_stop_loss = AsyncMock()
    # Make set_take_profit ALWAYS fail
    bot.exchange.set_take_profit = AsyncMock(side_effect=Exception("API Error"))

    bot._close_position = AsyncMock()
    open_pos = Position(
        {"symbol": "BTC/USDT", "side": "long", "contracts": 1.0, "entryPrice": 50000.0}
    )
    bot.exchange.get_position = AsyncMock(return_value=open_pos)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await bot._open_position("long", 50000.0, 10000.0, "test_reason")

    assert bot.exchange.set_stop_loss.call_count == 1
    assert bot.exchange.set_take_profit.call_count == 4
    assert mock_sleep.call_count == 3

    bot._close_position.assert_called_once_with(
        open_pos, 50000.0, "emergency_close_tp_placement_failed"
    )
    bot.database.log_trade_open.assert_not_called()


@pytest.mark.asyncio
async def test_open_position_success_with_retries(bot):
    bot.config.trading.symbol = "BTC/USDT"

    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )

    # Fail twice, then succeed
    bot.exchange.set_stop_loss = AsyncMock(
        side_effect=[Exception("Fail 1"), Exception("Fail 2"), None]
    )
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
    position = Position(
        {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
            "notional": 50000.0,
            "unrealizedPnl": 0.0,
            "leverage": 1,
            "liquidationPrice": 0.0,
        }
    )

    current_price = 51000.0  # Expected price

    # Mock close_position to return an order with a different average price
    bot.exchange.close_position = AsyncMock(
        return_value={
            "id": "123",
            "average": 50900.0,  # Actual fill price (worse than expected)
            "price": 50900.0,
            "filled": 1.0,
        }
    )

    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50900.0,
            "total_fee": 0.0,
            "fee_currency": "USDT",
            "timestamp": 1234567890,
        }
    )

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
        "stop_loss": 49000.0,
    }
    bot.database.get_last_trade = AsyncMock(return_value=last_trade)

    position = Position()  # Flat position

    # Mock fetch_my_trades to return a closing trade
    closing_trade = {
        "timestamp": datetime(2023, 1, 1, 13, 0, 0, tzinfo=timezone.utc).timestamp()
        * 1000,
        "side": "sell",  # Closing side for LONG
        "amount": 1.0,
        "price": 50500.0,
    }
    bot.exchange.fetch_my_trades = AsyncMock(return_value=[closing_trade])
    bot.database.log_trade_close = AsyncMock()
    bot.notifier.send = AsyncMock()
    bot.exchange.get_ticker = AsyncMock()  # Should not be called if trade found
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
        "stop_loss": 49000.0,
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


@pytest.mark.asyncio
async def test_paper_mode_long_pnl_calculation():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        mock_config.return_value.trading.symbol = "BTC/USDT"

        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        # Setup paper position
        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 2.0,  # 2 BTC
            "entryPrice": 50000.0,
            "notional": 100000.0,
            "unrealizedPnl": 0.0,
            "leverage": 10,
            "liquidationPrice": 45000.0,
        }

        # Mock get_ticker for exit price
        exchange.get_ticker = AsyncMock(return_value={"last": 51000.0})

        # Call close_position
        order = await exchange.close_position("BTC/USDT")

        # PnL = (51000 - 50000) * 2.0 = 2000.0
        assert order["pnl"] == 2000.0
        assert exchange._paper_balance == 12000.0  # 10000 + 2000


@pytest.mark.asyncio
async def test_paper_mode_short_pnl_calculation():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        mock_config.return_value.trading.symbol = "BTC/USDT"

        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        # Setup paper position
        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "short",
            "contracts": 2.0,  # 2 BTC
            "entryPrice": 50000.0,
            "notional": 100000.0,
            "unrealizedPnl": 0.0,
            "leverage": 10,
            "liquidationPrice": 55000.0,
        }

        # Mock get_ticker for exit price (price went down, so short makes profit)
        exchange.get_ticker = AsyncMock(return_value={"last": 49000.0})

        # Call close_position
        order = await exchange.close_position("BTC/USDT")

        # PnL = (50000 - 49000) * 2.0 = 2000.0
        assert order["pnl"] == 2000.0
        assert exchange._paper_balance == 12000.0  # 10000 + 2000


def test_paper_mode_long_sl_trigger():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
        }

        exchange._paper_orders = [
            {
                "id": "sl_1",
                "symbol": "BTC/USDT",
                "type": "stop_market",
                "side": "sell",
                "stopPrice": 49000.0,
                "status": "open",
            }
        ]

        # Price goes down, hits SL
        exchange._check_paper_orders(49000.0)

        assert exchange._paper_position is None
        assert len(exchange._paper_orders) == 0
        assert exchange._paper_balance == 9000.0  # 10000 - 1000 loss


def test_paper_mode_long_tp_trigger():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
        }

        exchange._paper_orders = [
            {
                "id": "tp_1",
                "symbol": "BTC/USDT",
                "type": "take_profit_market",
                "side": "sell",
                "take_profit_price": 51000.0,
                "status": "open",
            }
        ]

        # Price goes up, hits TP
        exchange._check_paper_orders(51000.0)

        assert exchange._paper_position is None
        assert len(exchange._paper_orders) == 0
        assert exchange._paper_balance == 11000.0  # 10000 + 1000 profit


def test_paper_mode_short_sl_trigger():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "short",
            "contracts": 1.0,
            "entryPrice": 50000.0,
        }

        exchange._paper_orders = [
            {
                "id": "sl_1",
                "symbol": "BTC/USDT",
                "type": "stop_market",
                "side": "buy",
                "stopPrice": 51000.0,
                "status": "open",
            }
        ]

        # Price goes up, hits short SL
        exchange._check_paper_orders(51000.0)

        assert exchange._paper_position is None
        assert len(exchange._paper_orders) == 0
        assert exchange._paper_balance == 9000.0  # 10000 - 1000 loss


def test_paper_mode_short_tp_trigger():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "short",
            "contracts": 1.0,
            "entryPrice": 50000.0,
        }

        exchange._paper_orders = [
            {
                "id": "tp_1",
                "symbol": "BTC/USDT",
                "type": "take_profit_market",
                "side": "buy",
                "take_profit_price": 49000.0,
                "status": "open",
            }
        ]

        # Price goes down, hits short TP
        exchange._check_paper_orders(49000.0)

        assert exchange._paper_position is None
        assert len(exchange._paper_orders) == 0
        assert exchange._paper_balance == 11000.0  # 10000 + 1000 profit


def test_paper_mode_no_trigger_on_non_crossing_price():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        exchange = Exchange()
        exchange.paper_mode = True
        exchange._paper_balance = 10000.0

        exchange._paper_position = {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
        }

        exchange._paper_orders = [
            {
                "id": "sl_1",
                "symbol": "BTC/USDT",
                "type": "stop_market",
                "side": "sell",
                "stopPrice": 49000.0,
                "status": "open",
            },
            {
                "id": "tp_1",
                "symbol": "BTC/USDT",
                "type": "take_profit_market",
                "side": "sell",
                "take_profit_price": 51000.0,
                "status": "open",
            },
        ]

        # Price stays between SL and TP
        exchange._check_paper_orders(50500.0)

        assert exchange._paper_position is not None
        assert len(exchange._paper_orders) == 2
        assert exchange._paper_balance == 10000.0


@pytest.mark.asyncio
async def test_open_position_atr_stops(bot):
    bot.config.trading.symbol = "BTC/USDT"

    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    bot.risk.use_atr_stops = True
    bot.risk.calculate_atr_stops = MagicMock(return_value=(49000.0, 52000.0))

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )
    bot.exchange.set_stop_loss = AsyncMock()
    bot.exchange.set_take_profit = AsyncMock()

    bot._close_position = AsyncMock()
    bot.database.log_trade_open = AsyncMock()

    mock_ohlcv = MagicMock()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await bot._open_position(
            "long", 50000.0, 10000.0, "test_reason", ohlcv=mock_ohlcv
        )

    bot.risk.calculate_atr_stops.assert_called_once_with(50000.0, "long", mock_ohlcv)
    bot.exchange.set_stop_loss.assert_called_once_with("BTC/USDT", 49000.0, "long")
    bot.exchange.set_take_profit.assert_called_once_with("BTC/USDT", 52000.0, "long")


@pytest.mark.asyncio
async def test_open_position_fallback_fixed_stops(bot):
    bot.config.trading.symbol = "BTC/USDT"

    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    bot.risk.use_atr_stops = False
    bot.risk.calculate_stop_loss = MagicMock(return_value=48000.0)
    bot.risk.calculate_take_profit = MagicMock(return_value=53000.0)

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )
    bot.exchange.set_stop_loss = AsyncMock()
    bot.exchange.set_take_profit = AsyncMock()

    bot._close_position = AsyncMock()
    bot.database.log_trade_open = AsyncMock()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await bot._open_position("long", 50000.0, 10000.0, "test_reason", ohlcv=None)

    bot.risk.calculate_stop_loss.assert_called_once_with(50000.0, "long")
    bot.risk.calculate_take_profit.assert_called_once_with(50000.0, "long")
    bot.exchange.set_stop_loss.assert_called_once_with("BTC/USDT", 48000.0, "long")
    bot.exchange.set_take_profit.assert_called_once_with("BTC/USDT", 53000.0, "long")


@pytest.mark.asyncio
async def test_open_position_atr_stops_calculation_failure(bot):
    bot.config.trading.symbol = "BTC/USDT"

    bot.risk.validate_trade.return_value = MagicMock(approved=True, position_size=1.0)
    bot.risk.use_atr_stops = True

    # Mock to raise an exception, fallback to fixed stops
    bot.risk.calculate_atr_stops = MagicMock(
        side_effect=Exception("Data missing or malformed")
    )

    bot.risk.calculate_stop_loss = MagicMock(return_value=48000.0)
    bot.risk.calculate_take_profit = MagicMock(return_value=53000.0)

    bot.exchange.get_open_positions = AsyncMock(return_value=[])
    bot.exchange.market_long = AsyncMock(
        return_value={"id": "order123", "average": 50000.0}
    )
    bot.exchange.cancel_all_orders = AsyncMock()
    bot.exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 50000.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )
    bot.exchange.set_stop_loss = AsyncMock()
    bot.exchange.set_take_profit = AsyncMock()

    bot._close_position = AsyncMock()
    bot.database.log_trade_open = AsyncMock()

    mock_ohlcv = MagicMock()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await bot._open_position(
            "long", 50000.0, 10000.0, "test_reason", ohlcv=mock_ohlcv
        )

    bot.risk.calculate_atr_stops.assert_called_once_with(50000.0, "long", mock_ohlcv)
    bot.risk.calculate_stop_loss.assert_called_once_with(50000.0, "long")
    bot.risk.calculate_take_profit.assert_called_once_with(50000.0, "long")
    bot.exchange.set_stop_loss.assert_called_once_with("BTC/USDT", 48000.0, "long")
    bot.exchange.set_take_profit.assert_called_once_with("BTC/USDT", 53000.0, "long")


@pytest.mark.asyncio
async def test_market_long_invalid_amount():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        mock_config.return_value.trading.symbol = "BTC/USDT"
        exchange = Exchange()

        with pytest.raises(
            ValueError, match="market_long requires amount > 0, got None"
        ):
            await exchange.market_long(symbol="BTC/USDT", amount=None)

        with pytest.raises(ValueError, match="market_long requires amount > 0, got 0"):
            await exchange.market_long(symbol="BTC/USDT", amount=0)

        with pytest.raises(
            ValueError, match="market_long requires amount > 0, got -1.5"
        ):
            await exchange.market_long(symbol="BTC/USDT", amount=-1.5)


@pytest.mark.asyncio
async def test_market_short_invalid_amount():
    from src.exchange import Exchange

    with patch("src.exchange.get_config") as mock_config:
        mock_config.return_value.exchange.paper_mode = True
        mock_config.return_value.trading.symbol = "BTC/USDT"
        exchange = Exchange()

        with pytest.raises(
            ValueError, match="market_short requires amount > 0, got None"
        ):
            await exchange.market_short(symbol="BTC/USDT", amount=None)

        with pytest.raises(ValueError, match="market_short requires amount > 0, got 0"):
            await exchange.market_short(symbol="BTC/USDT", amount=0)

        with pytest.raises(
            ValueError, match="market_short requires amount > 0, got -1.5"
        ):
            await exchange.market_short(symbol="BTC/USDT", amount=-1.5)
