from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exchanges.base import Position
from src.main import OmniTrader
from src.risk import RiskManager
from src.strategy.base import Signal


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_liquidation_risk_trigger(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    # Setup
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.trading.timeframe = "1h"
    bot.config.trading.ohlcv_limit = 100

    # Mock Balance
    bot.exchange.get_balance.return_value = {
        "total": 10000.0,
        "free": 10000.0,
        "used": 0.0,
    }

    # Initialize Risk Manager with buffer
    bot.risk = RiskManager()
    bot.risk.liquidation_buffer_pct = 0.5  # 50%
    bot.risk.max_daily_loss_pct = 5.0
    await bot.risk.initialize_daily_stats(10000.0)

    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_timeframes = ["1h"]
    bot.strategy.required_candles = 100
    bot.strategy.analyze.return_value = MagicMock(signal=Signal.HOLD, indicators={})

    # Mock WS Feed to prevent staleness
    bot.ws_feed = MagicMock()
    bot.ws_feed.ticker_age.return_value = 10.0
    bot.ws_feed.latest_ticker.return_value = {"last": 44000.0}
    bot.ws_feed.latest_ohlcv.return_value = None

    # Mock OHLCV
    ohlcv_mock = MagicMock()
    ohlcv_mock.iloc = MagicMock()
    # Current price 45000
    ohlcv_mock.__getitem__.return_value.iloc.__getitem__.return_value = 45000.0
    # Need to mock the float conversion of close price in run_cycle
    # ohlcv["close"].iloc[-1]

    # Let's mock exchange.fetch_ohlcv to return a dataframe-like object
    import pandas as pd

    # Ensure DataFrame has a DatetimeIndex and necessary columns for Black Swan check
    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {"close": [45000.0], "high": [45000.0], "low": [44900.0]}, index=[now]
    )
    bot.exchange.fetch_ohlcv.return_value = df

    # Mock Position: Long from 50k, Liq 40k. Total dist 10k.
    # Current 45k. Dist to Liq 5k. 5k/10k = 0.5. Borderline.
    # Let's make it 44k. Dist to Liq 4k. 4k/10k = 0.4 < 0.5. Trigger.

    # Update df to 44k
    df = pd.DataFrame(
        {"close": [44000.0], "high": [44000.0], "low": [43900.0]}, index=[now]
    )
    bot.exchange.fetch_ohlcv.return_value = df

    position = Position(
        {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
            "liquidationPrice": 40000.0,
            "leverage": 10,
        }
    )
    bot.exchange.get_position.return_value = position

    # Mock close_position
    bot.exchange.close_position.return_value = {"id": "123", "average": 44000.0}
    # Fix: update mock to include average_price
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 44000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT",
    }

    # Mock database fee query
    bot.database.get_open_trade_fee = AsyncMock(return_value=2.0)
    bot.database.get_weekly_pnl = AsyncMock(return_value=0.0)

    # Run Cycle
    await bot.run_cycle()

    # Verify Close Called
    bot.exchange.close_position.assert_called_once()
    bot.database.log_trade_close.assert_called_once()
    assert (
        bot.database.log_trade_close.call_args[1]["reason"] == "liquidation_risk_exit"
    )


@pytest.mark.asyncio
@patch("src.database.factory.DatabaseFactory.get_database")
async def test_liquidation_risk_safe(mock_get_store):
    mock_get_store.return_value = AsyncMock()
    # Setup
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.trading.timeframe = "1h"
    bot.config.trading.ohlcv_limit = 100

    # Mock Balance
    bot.exchange.get_balance.return_value = {
        "total": 10000.0,
        "free": 10000.0,
        "used": 0.0,
    }

    # Initialize Risk Manager with buffer
    bot.risk = RiskManager()
    bot.risk.liquidation_buffer_pct = 0.5
    await bot.risk.initialize_daily_stats(10000.0)

    # Mock WS Feed to prevent staleness
    bot.ws_feed = MagicMock()
    bot.ws_feed.ticker_age.return_value = 10.0
    bot.ws_feed.latest_ticker.return_value = {"last": 48000.0}
    bot.ws_feed.latest_ohlcv.return_value = None

    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_timeframes = ["1h"]
    bot.strategy.required_candles = 100
    bot.strategy.analyze.return_value = MagicMock(signal=Signal.HOLD, indicators={})

    # Mock OHLCV
    import pandas as pd

    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {"close": [45000.0], "high": [45000.0], "low": [44900.0]}, index=[now]
    )
    bot.exchange.fetch_ohlcv.return_value = df

    # Mock Position: Long from 50k, Liq 40k. Total dist 10k.
    # Current 48k. Dist to Liq 8k. 8k/10k = 0.8 > 0.5. Safe.

    # Update df to 48k
    df = pd.DataFrame(
        {"close": [48000.0], "high": [48000.0], "low": [47900.0]}, index=[now]
    )
    bot.exchange.fetch_ohlcv.return_value = df

    position = Position(
        {
            "symbol": "BTC/USDT",
            "side": "long",
            "contracts": 1.0,
            "entryPrice": 50000.0,
            "liquidationPrice": 40000.0,
            "leverage": 10,
        }
    )
    bot.exchange.get_position.return_value = position
    bot.database.get_weekly_pnl = AsyncMock(return_value=0.0)

    # Run Cycle
    await bot.run_cycle()

    # Verify Close NOT Called
    bot.exchange.close_position.assert_not_called()
