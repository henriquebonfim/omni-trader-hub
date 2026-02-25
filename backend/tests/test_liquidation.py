from unittest.mock import AsyncMock, MagicMock
from src.main import OmniTrader
from src.risk import RiskManager
from src.exchange import Position
from src.strategies.base import Signal
import pytest

@pytest.mark.asyncio
async def test_liquidation_risk_trigger():
    # Setup
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.trading.ohlcv_limit = 100

    # Mock Balance
    bot.exchange.get_balance.return_value = {"total": 10000.0, "free": 10000.0, "used": 0.0}

    # Initialize Risk Manager with buffer
    bot.risk = RiskManager()
    bot.risk.liquidation_buffer_pct = 0.5 # 50%
    bot.risk.max_daily_loss_pct = 5.0
    bot.risk.initialize_daily_stats(10000.0)

    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_candles = 100
    bot.strategy.analyze.return_value = MagicMock(signal=Signal.HOLD, indicators={})

    # Mock OHLCV
    ohlcv_mock = MagicMock()
    ohlcv_mock.iloc = MagicMock()
    # Current price 45000
    ohlcv_mock.__getitem__.return_value.iloc.__getitem__.return_value = 45000.0
    # Need to mock the float conversion of close price in run_cycle
    # ohlcv["close"].iloc[-1]

    # Let's mock exchange.fetch_ohlcv to return a dataframe-like object
    import pandas as pd
    df = pd.DataFrame({"close": [45000.0]})
    bot.exchange.fetch_ohlcv.return_value = df

    # Mock Position: Long from 50k, Liq 40k. Total dist 10k.
    # Current 45k. Dist to Liq 5k. 5k/10k = 0.5. Borderline.
    # Let's make it 44k. Dist to Liq 4k. 4k/10k = 0.4 < 0.5. Trigger.

    # Update df to 44k
    df = pd.DataFrame({"close": [44000.0]})
    bot.exchange.fetch_ohlcv.return_value = df

    position = Position({
        "symbol": "BTC/USDT",
        "side": "long",
        "contracts": 1.0,
        "entryPrice": 50000.0,
        "liquidationPrice": 40000.0,
        "leverage": 10
    })
    bot.exchange.get_position.return_value = position

    # Mock close_position
    bot.exchange.close_position.return_value = {"id": "123", "average": 44000.0}
    # Fix: update mock to include average_price
    bot.exchange.get_order_fill_details.return_value = {
        "average_price": 44000.0,
        "total_fee": 1.0,
        "fee_currency": "USDT"
    }

    # Mock database last trade for fee calculation
    bot.database.get_last_trade.return_value = {"fee": 2.0}

    # Run Cycle
    await bot.run_cycle()

    # Verify Close Called
    bot.exchange.close_position.assert_called_once()
    bot.database.log_trade_close.assert_called_once()

@pytest.mark.asyncio
async def test_liquidation_risk_safe():
    # Setup
    bot = OmniTrader()
    bot.exchange = AsyncMock()
    bot.database = AsyncMock()
    bot.notifier = AsyncMock()
    bot.config = MagicMock()
    bot.config.trading.symbol = "BTC/USDT"
    bot.config.trading.ohlcv_limit = 100

    # Mock Balance
    bot.exchange.get_balance.return_value = {"total": 10000.0, "free": 10000.0, "used": 0.0}

    # Initialize Risk Manager with buffer
    bot.risk = RiskManager()
    bot.risk.liquidation_buffer_pct = 0.5
    bot.risk.initialize_daily_stats(10000.0)

    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_candles = 100
    bot.strategy.analyze.return_value = MagicMock(signal=Signal.HOLD, indicators={})

    # Mock OHLCV
    import pandas as pd
    df = pd.DataFrame({"close": [45000.0]})
    bot.exchange.fetch_ohlcv.return_value = df

    # Mock Position: Long from 50k, Liq 40k. Total dist 10k.
    # Current 48k. Dist to Liq 8k. 8k/10k = 0.8 > 0.5. Safe.

    # Update df to 48k
    df = pd.DataFrame({"close": [48000.0]})
    bot.exchange.fetch_ohlcv.return_value = df

    position = Position({
        "symbol": "BTC/USDT",
        "side": "long",
        "contracts": 1.0,
        "entryPrice": 50000.0,
        "liquidationPrice": 40000.0,
        "leverage": 10
    })
    bot.exchange.get_position.return_value = position

    # Run Cycle
    await bot.run_cycle()

    # Verify Close NOT Called
    bot.exchange.close_position.assert_not_called()
