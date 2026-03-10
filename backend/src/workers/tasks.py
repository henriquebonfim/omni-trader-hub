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
        raise self.retry(exc=exc, countdown=1) from exc


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
        raise self.retry(exc=exc, countdown=1) from exc


@celery_app.task(bind=True, name="omnitrader.ingest_news_cycle", max_retries=2)
def ingest_news_cycle(self) -> dict:
    """
    Run the news ingestion pipeline:
    1. Fetch CryptoPanic, Fear & Greed Index, and RSS feeds
    2. Enhance new news events with Ollama NLP.
    3. Prune old news events.

    Returns
    -------
    dict
        Summary of operations.
    """
    import asyncio

    from src.config import get_config
    from src.database import MemgraphDatabase
    from src.graph.ingestor import NewsIngestor
    from src.graph.nlp import OllamaNLP

    config = get_config()

    async def _run_pipeline():
        db = MemgraphDatabase(
            host=getattr(config.database, "host", "memgraph"),
            port=int(getattr(config.database, "port", 7687)),
            username=getattr(config.database, "username", ""),
            password=getattr(config.database, "password", ""),
            encrypted=getattr(config.database, "encrypted", False),
        )
        await db.connect()

        graph_config = getattr(config, "graph", None)
        api_key = (
            getattr(graph_config, "cryptopanic_api_key", None) if graph_config else None
        )

        ingestor = NewsIngestor(db=db, cryptopanic_api_key=api_key)

        # Parallel ingest operations
        results = await asyncio.gather(
            ingestor.fetch_cryptopanic(),
            ingestor.fetch_rss_feeds(),
            ingestor.fetch_fear_greed(),
            return_exceptions=True,
        )

        cryptopanic_events = results[0] if isinstance(results[0], list) else []
        rss_events = results[1] if isinstance(results[1], list) else []

        all_new_events = cryptopanic_events + rss_events

        model = (
            getattr(graph_config, "ollama_model", "llama3:8b")
            if graph_config
            else "llama3:8b"
        )
        timeout = (
            int(getattr(graph_config, "ollama_timeout", 30)) if graph_config else 30
        )

        nlp = OllamaNLP(model=model, timeout=timeout)

        enriched_count = 0
        semaphore = asyncio.Semaphore(5)

        async def _enrich_with_semaphore(event_id: str):
            async with semaphore:
                try:
                    await nlp.enrich_news_event(event_id, db)
                    return True
                except Exception as e:
                    logger.error(f"Failed to enrich event {event_id}: {e}")
                    return False

        enrichment_tasks = [
            _enrich_with_semaphore(event_id) for event_id in all_new_events
        ]
        results = await asyncio.gather(*enrichment_tasks)
        enriched_count = sum(1 for r in results if r)

        await nlp.close()

        days_to_keep = (
            int(getattr(graph_config, "news_ttl_days", 7)) if graph_config else 7
        )
        await ingestor.prune_old_news(days=days_to_keep)

        await db.close()

        return {
            "cryptopanic_events": len(cryptopanic_events),
            "rss_events": len(rss_events),
            "enriched_events": enriched_count,
        }

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(_run_pipeline())
        logger.info("ingest_news_cycle_completed", result=result)
        return result
    except Exception as exc:
        logger.error("ingest_news_cycle_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=5) from exc


@celery_app.task(bind=True, name="omnitrader.analyze_knowledge_graph", max_retries=1)
def analyze_knowledge_graph(
    self, symbol: str, current_price: float, config_dict: dict
) -> dict:
    """
    Compute graph analytics metrics (sentiment, contagion, divergence) in Celery.
    Returns JSON-serializable dict with crisis signals.
    """
    import asyncio

    try:
        from src.database import DatabaseFactory
        from src.graph.analytics import GraphAnalytics

        # Helper inner async func
        async def _run_analytics():
            config = _build_config(config_dict)
            db = DatabaseFactory.get_database(config)
            await db.connect()

            try:
                ga = GraphAnalytics(db)

                sentiment = await ga.get_asset_sentiment(symbol, hours_lookback=24)
                contagion = await ga.detect_sector_contagion(symbol, hours_lookback=24)
                divergence = await ga.detect_sentiment_divergence(
                    symbol, current_price, hours_lookback=24
                )

                return {
                    "sentiment": sentiment,
                    "contagion": contagion,
                    "divergence": divergence,
                }
            finally:
                await db.close()

        # Run async logic synchronously for Celery
        return asyncio.run(_run_analytics())

    except Exception as exc:
        logger.error(
            "analyze_knowledge_graph_task_failed", error=str(exc), symbol=symbol
        )
        raise self.retry(exc=exc, countdown=1) from exc
