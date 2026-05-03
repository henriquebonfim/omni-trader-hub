import pytest
from unittest.mock import AsyncMock
from src.application.backtest.walk_forward import WalkForwardRunner
from src.domain.strategy.base import BaseStrategy
from src.config import Config

class MockStrategy(BaseStrategy):
    required_candles = 1
    def analyze(self, **kwargs): pass
    @property
    def metadata(self): return {}
    def should_long(self): return False
    def should_short(self): return False
    def should_exit(self): return False
    @property
    def valid_regimes(self): return []
    def update(self, config): pass

@pytest.mark.asyncio
async def test_walk_forward_runner():
    mock_config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "1h"},
        "backtest": {},
        "risk": {},
    }
    config = Config(mock_config_data)
    strategy = MockStrategy(config)
    
    mock_exchange = AsyncMock()
    # Mock data to cover roughly 8 months for a 6+1 split
    mock_candles = [
        {"timestamp": i * 3600000, "close": 100 + i * 0.1}
        for i in range(24 * 30 * 8)
    ]
    mock_exchange.fetch_candles.return_value = mock_candles
    
    runner = WalkForwardRunner(
        config=config,
        strategy=strategy,
        exchange=mock_exchange,
        initial_balance=10000.0
    )
    
    # Mock engine to return predictable results
    runner.engine.run = lambda candles: {
        "metrics": {"sharpe_ratio": 1.5, "profit_factor": 1.2, "win_rate": 0.6, "net_profit": 100.0},
        "trades": [], "signals": [], "equity_curve": []
    }
    
    results = await runner.run(
        symbol="BTC/USDT",
        timeframe="1h",
        start_date="2023-01-01",
        end_date="2023-08-31",
        train_months=6,
        test_months=1,
    )
    
    assert "summary" in results
    assert "results" in results
    
    # With 8 months of data and a 6+1 split, we should get at least 1 split
    assert len(results["results"]) >= 1
    
    summary = results["summary"]
    assert summary["num_splits"] >= 1
    assert summary["avg_sharpe"] == 1.5
    assert summary["avg_profit_factor"] == 1.2
    assert summary["avg_win_rate"] == 0.6
    assert summary["total_net_profit"] > 0
