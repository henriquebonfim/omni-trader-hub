"""
Tests for Celery workers: tasks, serializers, and async dispatch.

All Celery tasks run in **eager mode** (synchronous, no broker required)
so these tests pass in CI and local environments without Redis.
"""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.workers import celery_app
from src.workers.serializers import (
    df_to_json,
    json_to_df,
    json_to_market_data,
    market_data_to_json,
)
from src.workers.tasks import analyze_regime, analyze_strategy


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def celery_eager(monkeypatch):
    """Run all Celery tasks synchronously (no broker needed)."""
    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)
    yield
    celery_app.conf.update(task_always_eager=False)


def _make_ohlcv(n: int = 60) -> pd.DataFrame:
    """Generate synthetic OHLCV DataFrame."""
    import numpy as np

    rng = pd.date_range("2025-01-01", periods=n, freq="5min")
    close = 50000 + np.cumsum(np.random.randn(n) * 100)
    df = pd.DataFrame(
        {
            "open": close - 50,
            "high": close + 100,
            "low": close - 100,
            "close": close,
            "volume": np.abs(np.random.randn(n)) * 1000 + 500,
        },
        index=rng,
    )
    df.index.name = "timestamp"
    return df


def _make_config_dict() -> dict:
    """Minimal config dict matching EMAVolumeStrategy requirements."""
    return {
        "strategy": {
            "name": "ema_volume",
            "ema_fast": 9,
            "ema_slow": 21,
            "volume_sma": 20,
            "volume_threshold": 1.2,
            "trend_filter_enabled": False,
            "trend_timeframe": "4h",
        },
        "trading": {
            "symbol": "BTC/USDT:USDT",
            "timeframe": "5m",
            "ohlcv_limit": 100,
        },
        "risk": {
            "max_position_size_pct": 5.0,
            "stop_loss_pct": 1.0,
        },
    }


# ---------------------------------------------------------------------------
# Serializer tests
# ---------------------------------------------------------------------------


def test_df_round_trip():
    """DataFrame → JSON → DataFrame preserves shape and values."""
    df = _make_ohlcv(20)
    json_str = df_to_json(df)
    restored = json_to_df(json_str)

    assert restored.shape == df.shape
    assert list(restored.columns) == list(df.columns)
    assert abs(restored["close"].iloc[-1] - df["close"].iloc[-1]) < 1e-6


def test_df_round_trip_index_is_datetime():
    """Round-tripped DataFrame should have a DatetimeIndex."""
    df = _make_ohlcv(20)
    restored = json_to_df(df_to_json(df))
    assert isinstance(restored.index, pd.DatetimeIndex)


def test_market_data_round_trip():
    """Multi-timeframe market_data dict round-trips correctly."""
    market_data = {
        "5m": _make_ohlcv(60),
        "15m": _make_ohlcv(30),
    }
    json_str = market_data_to_json(market_data)
    restored = json_to_market_data(json_str)

    assert set(restored.keys()) == {"5m", "15m"}
    assert restored["5m"].shape == market_data["5m"].shape
    assert restored["15m"].shape == market_data["15m"].shape


def test_market_data_json_is_valid_json():
    market_data = {"5m": _make_ohlcv(10)}
    json_str = market_data_to_json(market_data)
    parsed = json.loads(json_str)
    assert "5m" in parsed
    assert "columns" in parsed["5m"]


# ---------------------------------------------------------------------------
# analyze_regime task tests
# ---------------------------------------------------------------------------


def test_analyze_regime_returns_string():
    """Task should return a MarketRegime value string."""
    from src.analysis.regime import MarketRegime

    ohlcv = _make_ohlcv(60)
    result = analyze_regime.apply(args=(df_to_json(ohlcv),)).get()

    assert isinstance(result, str)
    valid_values = {r.value for r in MarketRegime}
    assert result in valid_values


def test_analyze_regime_short_data_returns_uncertain():
    """Too-short OHLCV should return 'uncertain'."""
    ohlcv = _make_ohlcv(5)  # Too few candles for ADX
    result = analyze_regime.apply(args=(df_to_json(ohlcv),)).get()
    assert result == "uncertain"


# ---------------------------------------------------------------------------
# analyze_strategy task tests
# ---------------------------------------------------------------------------


def test_analyze_strategy_returns_expected_keys():
    """Task result must contain signal, reason, and indicators."""
    market_data = {"5m": _make_ohlcv(60)}
    result = analyze_strategy.apply(
        args=(
            "ema_volume",
            _make_config_dict(),
            market_data_to_json(market_data),
            None,
            "neutral",
        )
    ).get()

    assert "signal" in result
    assert "reason" in result
    assert "indicators" in result


def test_analyze_strategy_signal_is_valid():
    """signal value must be a valid Signal enum member."""
    from src.strategies import Signal

    market_data = {"5m": _make_ohlcv(60)}
    result = analyze_strategy.apply(
        args=(
            "ema_volume",
            _make_config_dict(),
            market_data_to_json(market_data),
            None,
            "neutral",
        )
    ).get()

    valid_signals = {s.value for s in Signal}
    assert result["signal"] in valid_signals


def test_analyze_strategy_with_open_position():
    """Task should handle a current_side of 'long' without error."""
    market_data = {"5m": _make_ohlcv(60)}
    result = analyze_strategy.apply(
        args=(
            "ema_volume",
            _make_config_dict(),
            market_data_to_json(market_data),
            "long",
            "bullish",
        )
    ).get()
    assert "signal" in result


def test_analyze_strategy_indicators_are_json_serializable():
    """Indicators dict must contain only JSON-serializable Python types."""
    market_data = {"5m": _make_ohlcv(60)}
    result = analyze_strategy.apply(
        args=(
            "ema_volume",
            _make_config_dict(),
            market_data_to_json(market_data),
            None,
            "neutral",
        )
    ).get()

    # Should not raise
    serialized = json.dumps(result["indicators"])
    assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# Celery app configuration test
# ---------------------------------------------------------------------------


def test_celery_app_broker_uses_redis():
    """Broker URL should point at redis DB 1."""
    # Reset to real config for this test
    celery_app.conf.update(task_always_eager=False)
    assert "redis" in celery_app.conf.broker_url
    assert "/1" in celery_app.conf.broker_url
    celery_app.conf.update(task_always_eager=True)


def test_celery_result_backend_uses_redis():
    celery_app.conf.update(task_always_eager=False)
    assert "redis" in celery_app.conf.result_backend
    assert "/2" in celery_app.conf.result_backend
    celery_app.conf.update(task_always_eager=True)
