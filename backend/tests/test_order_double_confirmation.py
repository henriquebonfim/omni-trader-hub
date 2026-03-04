from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import Config
from src.exchange import Exchange
from src.main import OmniTrader


@pytest.mark.asyncio
async def test_order_fill_confirmation_success():
    # Setup
    config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "15min"},
        "strategy": {"bias_confirmation": False},
        "exchange": {"paper_mode": True},
    }
    config = Config(config_data)

    with (
        patch("src.exchange.ccxt.binance"),
        patch("src.exchange.get_config", return_value=config),
    ):
        exchange = Exchange()
        exchange.paper_mode = False  # Force non-paper mode for trade fetching logic

        # Mock fetch_my_trades to return trades for the order
        mock_trades = [
            {
                "order": "123",
                "amount": 0.5,
                "price": 50000.0,
                "cost": 25000.0,
                "fee": {"cost": 10, "currency": "USDT"},
            },
            {
                "order": "123",
                "amount": 0.5,
                "price": 51000.0,
                "cost": 25500.0,
                "fee": {"cost": 10, "currency": "USDT"},
            },
        ]
        exchange.fetch_my_trades = AsyncMock(return_value=mock_trades)

        result = await exchange.get_order_fill_details("123", "BTC/USDT")

        assert result["confirmed"] is True
        assert result["average_price"] == 50500.0
        assert result["total_fee"] == 20.0


@pytest.mark.asyncio
async def test_order_fill_confirmation_timeout():
    config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "15min"},
        "strategy": {"bias_confirmation": False},
        "exchange": {"paper_mode": True},
    }
    config = Config(config_data)

    with (
        patch("src.exchange.ccxt.binance"),
        patch("src.exchange.get_config", return_value=config),
    ):
        exchange = Exchange()
        exchange.paper_mode = False

        # Mock fetch_my_trades to always return empty
        exchange.fetch_my_trades = AsyncMock(return_value=[])

        # Use small retries and delay to speed up test
        result = await exchange.get_order_fill_details(
            "123", "BTC/USDT", retries=2, delay=0.1
        )

        assert result["confirmed"] is False
        assert result["average_price"] == 0.0


@pytest.mark.asyncio
async def test_bot_logs_warning_on_unconfirmed_fill():
    # Setup bot with mocked exchange
    with (
        patch("src.main.Exchange") as MockExchange,
        patch("src.main.DatabaseFactory"),
        patch("src.main.RiskManager") as MockRiskManager,
        patch("src.main.Notifier") as MockNotifier,
        patch("src.main.get_config") as mock_get_config,
        patch("src.main.get_strategy"),
    ):
        MockNotifier.return_value = AsyncMock()
        mock_config = MagicMock()
        mock_config.trading.symbol = "BTC/USDT"
        mock_get_config.return_value = mock_config

        bot = OmniTrader()
        bot.exchange = MockExchange()

        # Mock risk check approved
        MockRiskManager.return_value.validate_trade.return_value.approved = True
        MockRiskManager.return_value.validate_trade.return_value.position_size = 1.0

        # Mock order placement
        bot.exchange.market_long = AsyncMock(return_value={"id": "123"})

        # Mock UNCONFIRMED fill
        bot.exchange.get_order_fill_details = AsyncMock(
            return_value={
                "average_price": 50000.0,
                "total_fee": 10.0,
                "fee_currency": "USDT",
                "confirmed": False,  # <--- UNCONFIRMED
            }
        )

        # Mock other stuff to avoid errors
        bot.exchange.get_open_positions = AsyncMock(return_value=[])
        bot.exchange.cancel_all_orders = AsyncMock()
        bot.exchange.set_stop_loss = AsyncMock()
        bot.exchange.set_take_profit = AsyncMock()
        bot.database.log_trade_open = AsyncMock()

        with patch("src.main.logger") as mock_logger:
            await bot._open_position("long", 50000.0, 10000.0)

            # Check if warning was logged
            mock_logger.warning.assert_any_call(
                "order_fill_not_confirmed", order_id="123", symbol="BTC/USDT"
            )
