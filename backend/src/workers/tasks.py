"""
Celery tasks for OmniTrader.

Heavy Pandas/NumPy indicator calculations run here, in a separate worker
process, so the FastAPI / trading-loop event loop is never blocked.

Tasks
-----
analyze_strategy
    Run strategy.analyze() in a worker process.  Accepts and returns plain
    JSON-serializable data so nothing special is needed for Celery serialization.

analyze_regime
    Run RegimeClassifier.analyze() in a worker process.

Both tasks are **idempotent** (read-only, stateless) — safe to retry.
"""

import structlog

from src.workers import celery_app
from src.workers.serializers import json_to_df, json_to_market_data

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_config(config_dict: dict):
    """
    Reconstruct a lightweight config-like object from a plain dict.

    We pass only the fields the strategy and regime classifier need, rather
    than the entire YAML config, to keep the payload small.
    """
    from types import SimpleNamespace

    def _ns(d):
        if isinstance(d, dict):
            return SimpleNamespace(**{k: _ns(v) for k, v in d.items()})
        return d

    return _ns(config_dict)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


@celery_app.task(bind=True, name="omnitrader.analyze_strategy", max_retries=2)
def analyze_strategy(
    self,
    strategy_name: str,
    config_dict: dict,
    market_data_json: str,
    current_side: str | None,
    market_trend: str = "neutral",
) -> dict:
    """
    Run strategy indicator analysis in a Celery worker.

    Parameters
    ----------
    strategy_name:
        Registered strategy name (e.g. ``"ema_volume"``).
    config_dict:
        Serialized config subset required by the strategy.
    market_data_json:
        JSON string produced by :func:`~src.workers.serializers.market_data_to_json`.
    current_side:
        Current open position side (``"long"``, ``"short"``, or ``None``).
    market_trend:
        Higher-timeframe trend string (``"bullish"``, ``"bearish"``, ``"neutral"``).

    Returns
    -------
    dict
        ``{"signal": str, "reason": str, "indicators": dict}``
    """
    try:
        from src.strategies import get_strategy

        market_data = json_to_market_data(market_data_json)
        config = _build_config(config_dict)

        strategy_class = get_strategy(strategy_name)
        strategy = strategy_class(config)

        result = strategy.analyze(market_data, current_side, market_trend=market_trend)

        # Sanitize numpy scalars for JSON serialization
        def _sanitize(v):
            if hasattr(v, "item"):
                return v.item()
            if isinstance(v, dict):
                return {k: _sanitize(val) for k, val in v.items()}
            if isinstance(v, list):
                return [_sanitize(i) for i in v]
            return v

        return {
            "signal": result.signal.value,
            "reason": result.reason,
            "indicators": _sanitize(result.indicators),
        }

    except Exception as exc:
        logger.error(
            "analyze_strategy_task_failed", error=str(exc), strategy=strategy_name
        )
        raise self.retry(exc=exc, countdown=1)


@celery_app.task(bind=True, name="omnitrader.analyze_regime", max_retries=2)
def analyze_regime(self, ohlcv_json: str) -> str:
    """
    Run RegimeClassifier in a Celery worker.

    Parameters
    ----------
    ohlcv_json:
        JSON string produced by :func:`~src.workers.serializers.df_to_json`.

    Returns
    -------
    str
        :class:`~src.analysis.regime.MarketRegime` value string.
    """
    try:
        from src.analysis.regime import RegimeClassifier

        ohlcv = json_to_df(ohlcv_json)
        classifier = RegimeClassifier()
        regime = classifier.analyze(ohlcv)
        return regime.value

    except Exception as exc:
        logger.error("analyze_regime_task_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=1)
