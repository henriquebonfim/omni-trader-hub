from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.main import OmniTrader


@pytest.mark.asyncio
@patch("src.main.date")
@patch("src.main.get_config")
async def test_run_cycle_ws_stale_fallback(mock_get_config, mock_date):
    # Setup bot
    mock_get_config.return_value.strategy.name = "ema_volume"
    mock_get_config.return_value.trading.symbol = "BTC/USDT"
    bot = OmniTrader()
    
    # Mock Risk & Circuit Breaker logic to pass smoothly
    bot.risk = MagicMock()
    bot.risk.check_circuit_breaker.return_value = False
    bot.risk.check_weekly_circuit_breaker = AsyncMock(return_value=False)
    bot.risk._weekly_circuit_breaker_active = False
    bot.risk.daily_stats = MagicMock()
    bot.risk.daily_stats.realized_pnl = 0
    bot.risk.daily_stats.pnl_pct = 0
    bot.risk.initialize_daily_stats = AsyncMock()
    bot.risk.check_black_swan.return_value = False
    bot.exchange.fetch_funding_rate = AsyncMock(return_value=0.0)
    bot.config.trading.ohlcv_limit = 100
    bot.database.get_weekly_pnl = AsyncMock(return_value=0.0)
    
    # Mock Exchange
    bot.exchange = AsyncMock()
    bot.exchange.get_balance.return_value = {"total": 1000, "free": 1000}
    
    mock_position = MagicMock()
    mock_position.is_open = False
    bot.exchange.get_position.return_value = mock_position
    
    # Needs to be called so current_price relies on REST ticker
    bot.exchange.get_ticker.return_value = {"last": 45000.0}
    
    bot.exchange.fetch_ohlcv = AsyncMock()
    
    # Mock Database
    bot.database = AsyncMock()
    
    # Mock Notifier
    bot.notifier = AsyncMock()
    
    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_timeframes = ["15m"]
    bot.strategy.required_candles = 100
    
    # Mock WS Feed indicating staleness (> 60, < 120)
    bot.ws_feed = MagicMock()
    bot.ws_feed.ticker_age.return_value = 65.0
    bot.ws_feed.latest_ticker.return_value = {"last": 44000.0}  # Shouldn't be used
    
    # Mock Pandas DF for OHLCV
    import pandas as pd
    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {"close": [43000.0], "high": [43000.0], "low": [42900.0]}, index=[now]
    )
    bot.ws_feed.latest_ohlcv.return_value = df
    bot.exchange.fetch_ohlcv = AsyncMock(return_value=df)
    bot.strategy.required_candles = 1
    
    # Mock Workers to avoid real Celery logic
    with patch("src.main.dispatch") as mock_dispatch:
        mock_dispatch.return_value = ({"signal": "HOLD", "reason": "test", "indicators": {}}, "trending")
        
        await bot.run_cycle()
    
    # Verify fallback to REST was called
    bot.exchange.get_ticker.assert_called_once_with(bot.config.trading.symbol)
    
@pytest.mark.asyncio
@patch("src.main.date")
@patch("src.main.get_config")
async def test_run_cycle_ws_extremely_stale_pause(mock_get_config, mock_date):
    # Setup bot
    mock_get_config.return_value.strategy.name = "ema_volume"
    mock_get_config.return_value.trading.symbol = "BTC/USDT"
    bot = OmniTrader()
    
    # Mock Risk
    bot.risk = MagicMock()
    bot.risk.check_circuit_breaker.return_value = False
    bot.risk.check_weekly_circuit_breaker = AsyncMock(return_value=False)
    bot.risk._weekly_circuit_breaker_active = False
    bot.risk.daily_stats = MagicMock()
    bot.risk.daily_stats.realized_pnl = 0
    bot.risk.daily_stats.pnl_pct = 0
    bot.risk.initialize_daily_stats = AsyncMock()
    bot.risk.check_black_swan.return_value = False
    bot.exchange.fetch_funding_rate = AsyncMock(return_value=0.0)
    bot.config.trading.ohlcv_limit = 100
    bot.database.get_weekly_pnl = AsyncMock(return_value=0.0)
    
    # Mock Exchange
    bot.exchange = AsyncMock()
    bot.exchange.get_balance.return_value = {"total": 1000, "free": 1000}
    
    mock_position = MagicMock()
    mock_position.is_open = False
    bot.exchange.get_position.return_value = mock_position
    
    # Mock Database
    bot.database = AsyncMock()
    
    # Mock Notifier
    bot.notifier = AsyncMock()
    
    # Mock Strategy
    bot.strategy = MagicMock()
    bot.strategy.required_timeframes = ["15m"]
    bot.strategy.required_candles = 100
    
    # Mock WS Feed indicating extreme staleness (> 120)
    bot.ws_feed = MagicMock()
    bot.ws_feed.ticker_age.return_value = 125.0
    
    # Mock Pandas DF for OHLCV
    import pandas as pd
    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {"close": [43000.0], "high": [43000.0], "low": [42900.0]}, index=[now]
    )
    bot.ws_feed.latest_ohlcv.return_value = df
    bot.exchange.fetch_ohlcv = AsyncMock(return_value=df)
    bot.strategy.required_candles = 1
    
    # Run cycle
    await bot.run_cycle()
    
    # Verify pause triggered (Notifier sent alert)
    bot.notifier.send.assert_called_with("⚠️ **Stale Data Alert**: WS ticker is 125s old. Trading paused.")
    
    # Ensure cycle stopped before strategy execution by checking if get_ticker or dispatch was called
    bot.exchange.get_ticker.assert_not_called()

