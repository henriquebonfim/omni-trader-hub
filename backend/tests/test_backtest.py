import math
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.backtest.engine import BacktestEngine
from src.backtest.metrics import (
    bootstrap_confidence_intervals,
    calculate_metrics,
    generate_walk_forward_splits,
)
from src.config import Config
from src.database.memgraph import MemgraphDatabase
from src.strategy.bollinger_bands import BollingerBandsStrategy


def test_metrics_calculation():
    trades = [
        {"pnl": 10.0, "pnl_pct": 0.01},
        {"pnl": -5.0, "pnl_pct": -0.005},
        {"pnl": 15.0, "pnl_pct": 0.015},
    ]
    metrics = calculate_metrics(trades, 1000.0)
    assert metrics["total_trades"] == 3
    assert metrics["win_rate"] == pytest.approx(2 / 3)
    assert metrics["profit_factor"] == 5.0  # 25 / 5
    assert metrics["net_profit"] == 20.0
    assert metrics["final_balance"] == 1020.0
    assert metrics["max_win_streak"] == 1
    assert metrics["max_loss_streak"] == 1


def test_bootstrap_ci():
    trades = [{"pnl": float(i)} for i in range(-5, 15)]
    ci = bootstrap_confidence_intervals(trades, iterations=100)
    assert "net_profit_ci_lower" in ci
    assert "net_profit_ci_upper" in ci
    assert ci["net_profit_ci_lower"] <= ci["net_profit_ci_upper"]


def test_walk_forward_splits():
    # 8 months of data
    day_ms = 24 * 3600 * 1000
    now = 1600000000000
    candles = [{"timestamp": now + i * day_ms} for i in range(240)]

    splits = generate_walk_forward_splits(candles, train_months=6, test_months=1)
    assert len(splits) > 0
    first_split = splits[0]
    assert len(first_split["train"]) > len(first_split["test"])
    assert first_split["train_end"] == first_split["test_start"]


def test_backtest_engine():
    config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "1h", "fee_rate": 0.001},
        "risk": {
            "max_position_size_pct": 10.0,
            "stop_loss_pct": 2.0,
            "take_profit_pct": 5.0,
        },
        "strategy": {"type": "bollinger_bands"},
    }
    config = Config(config_data)
    strategy = BollingerBandsStrategy(config)
    engine = BacktestEngine(strategy, config, initial_balance=10000.0)

    # Generate test candles
    candles = []
    now = 1600000000000
    # Create simple upward trend with a few dips
    for i in range(200):
        # We need the bollinger band to trigger, so make it oscillate
        val = 100 + math.sin(i / 5.0) * 10 + i * 0.1
        candles.append(
            {
                "timestamp": now + i * 3600000,
                "open": val - 1,
                "high": val + 2,
                "low": val - 2,
                "close": val,
                "volume": 100,
            }
        )

    res = engine.run(candles)

    assert "metrics" in res
    assert "trades" in res
    assert "signals" in res
    assert "equity_curve" in res
    assert res["metrics"]["final_balance"] > 0
    assert len(res["equity_curve"]) == 200


@pytest.mark.asyncio
async def test_memgraph_candle_storage(monkeypatch):
    # Mock driver
    mock_session = AsyncMock()
    mock_result = AsyncMock()

    mock_result.fetch.return_value = [
        {
            "timestamp": 1000,
            "open": 1.0,
            "high": 2.0,
            "low": 0.5,
            "close": 1.5,
            "volume": 100,
        }
    ]
    mock_session.run.return_value = mock_result
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    mock_driver = MagicMock()
    mock_driver.session.return_value = mock_session

    db = MemgraphDatabase()
    db._driver = mock_driver

    candles = [
        {
            "timestamp": 1000,
            "open": 1.0,
            "high": 2.0,
            "low": 0.5,
            "close": 1.5,
            "volume": 100,
        }
    ]

    saved = await db.save_candles("BTC", "1h", candles)
    assert saved == 1

    fetched = await db.get_candles("BTC", "1h")
    assert len(fetched) == 1
    assert fetched[0]["timestamp"] == 1000
    assert fetched[0]["open"] == 1.0
