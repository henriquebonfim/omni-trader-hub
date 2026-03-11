import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
import pandas as pd

from src.strategy.selector import StrategySelector, StrategyScore
from src.intelligence.regime import MarketRegime
from src.main import OmniTrader
from src.config import get_config

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # Mock for driver session / run / data
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[
        {
            "name": "ema_volume",
            "sample_size": 30,
            "sharpe": 1.5,
            "profit_factor": 1.2,
            "win_rate": 0.55
        },
        {
            "name": "breakout",
            "sample_size": 25,
            "sharpe": 2.0,
            "profit_factor": 1.5,
            "win_rate": 0.60
        }
    ])
    mock_session.run = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    
    mock_driver = MagicMock()
    mock_driver.session.return_value = mock_session
    db._driver = mock_driver
    return db

@pytest.mark.asyncio
async def test_selector_scoring(mock_db):
    selector = StrategySelector(database=mock_db)
    
    # breakout:
    # norm_sharpe = min(max(2.0/3.0, 0), 1) = 0.666
    # norm_pf = min(max((1.5-1.0)/2.0, 0), 1) = 0.25
    # norm_wr = 0.60
    # composite: (0.4 * 0.666) + (0.3 * 0.25) + (0.3 * 0.6) = 0.266 + 0.075 + 0.18 = 0.521
    
    # ema_volume:
    # norm_sharpe = min(max(1.5/3.0, 0), 1) = 0.5
    # norm_pf = min(max((1.2-1.0)/2.0, 0), 1) = 0.1
    # norm_wr = 0.55
    # composite: (0.4 * 0.5) + (0.3 * 0.1) + (0.3 * 0.55) = 0.2 + 0.03 + 0.165 = 0.395
    
    scores = await selector.get_strategy_performance(MarketRegime.TRENDING)
    assert len(scores) == 2
    
    # Sort check
    scores.sort(key=lambda s: (s.composite_score, s.sample_size), reverse=True)
    assert scores[0].name == "breakout"
    assert scores[1].name == "ema_volume"
    
    best = await selector.get_best_strategy(MarketRegime.TRENDING)
    assert best == "breakout"

@pytest.mark.asyncio
async def test_selector_fallback(mock_db):
    # Setup mock to return empty
    mock_db._driver.session.return_value.__aenter__.return_value.run.return_value.data.return_value = []
    
    selector = StrategySelector(database=mock_db)
    best = await selector.get_best_strategy(MarketRegime.TRENDING)
    assert best == "adx_trend"

@pytest.mark.asyncio
async def test_omnitrader_strategy_auto_selection():
    config = get_config()
    config.strategy.mode = "auto"
    config.strategy.name = "ema_volume"
    
    bot = OmniTrader(config=config)
    bot.strategy_selector.get_best_strategy = AsyncMock(return_value="breakout")
    
    market_data = {"15m": pd.DataFrame()}
    primary_ohlcv = pd.DataFrame({"close": [1, 2, 3]})
    current_price = 3.0
    current_side = None
    market_trend = "neutral"
    
    # Force cooldown pass
    bot.last_strategy_rotation = datetime.now(timezone.utc) - timedelta(hours=5)
    
    bot.crisis_manager.is_crisis_active = AsyncMock(return_value=False)
    
    # Mock regimet classifier/celery
    from src.workers.tasks import analyze_regime, analyze_strategy, analyze_knowledge_graph
    import src.main as main_module
    
    async def mock_dispatch(task, *args, **kwargs):
        if task == analyze_regime:
            return MarketRegime.TRENDING.value
        if task == analyze_strategy:
            return {"signal": "hold", "reason": "test", "indicators": {}}
        if task == analyze_knowledge_graph:
            return {}
        return None
        
    main_module.dispatch = mock_dispatch
    
    await bot._analyze_cycle(
        symbol="BTC",
        market_data=market_data,
        primary_ohlcv=primary_ohlcv,
        current_price=current_price,
        current_side=current_side,
        market_trend=market_trend
    )
    
    # Assert strategy rotated
    assert bot.config.strategy.name == "breakout"
    assert isinstance(bot.strategy, type(bot.strategy))

@pytest.mark.asyncio
async def test_omnitrader_strategy_manual_override():
    config = get_config()
    config.strategy.mode = "manual"
    config.strategy.name = "ema_volume"
    
    bot = OmniTrader(config=config)
    bot.strategy_selector.get_best_strategy = AsyncMock(return_value="breakout")
    
    market_data = {"15m": pd.DataFrame()}
    primary_ohlcv = pd.DataFrame({"close": [1, 2, 3]})
    current_price = 3.0
    current_side = None
    market_trend = "neutral"
    
    # Force cooldown pass
    bot.last_strategy_rotation = datetime.now(timezone.utc) - timedelta(hours=5)
    
    bot.crisis_manager.is_crisis_active = AsyncMock(return_value=False)

    from src.workers.tasks import analyze_regime, analyze_strategy, analyze_knowledge_graph
    import src.main as main_module
    
    async def mock_dispatch(task, *args, **kwargs):
        if task == analyze_regime:
            return MarketRegime.TRENDING.value
        if task == analyze_strategy:
            return {"signal": "hold", "reason": "test", "indicators": {}}
        if task == analyze_knowledge_graph:
            return {}
        return None
        
    main_module.dispatch = mock_dispatch
    
    await bot._analyze_cycle(
        symbol="BTC",
        market_data=market_data,
        primary_ohlcv=primary_ohlcv,
        current_price=current_price,
        current_side=current_side,
        market_trend=market_trend
    )
    
    # Assert strategy DID NOT rotate because mode is manual
    assert bot.config.strategy.name == "ema_volume"
