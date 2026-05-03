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

from src.interfaces.workers import celery_app
from src.interfaces.workers.serializers import json_to_df, json_to_market_data

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
        JSON string produced by :func:`~src.interfaces.workers.serializers.market_data_to_json`.
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
        from src.domain.strategy import get_strategy
        from src.domain.strategy.custom_executor import CustomStrategyExecutor

        market_data = json_to_market_data(market_data_json)
        config = _build_config(config_dict)

        try:
            strategy_class = get_strategy(strategy_name)
            strategy = strategy_class(config)
        except ValueError:
            # Custom strategy fallback
            # We need to fetch from DB synchronously? We can't use async driver easily here unless we asyncio.run
            # Actually Celery tasks are sync. We should use a helper to fetch custom strategy or pass it in config
            import asyncio

            from src.infrastructure.database.factory import DatabaseFactory

            async def _fetch_custom(name):
                db = DatabaseFactory.get_database(config)
                await db.connect()
                cs = await db.get_custom_strategy(name)
                await db.close()
                return cs

            cs_data = asyncio.run(_fetch_custom(strategy_name))
            if not cs_data:
                raise ValueError(
                    f"Strategy {strategy_name} not found in registry or DB"
                ) from None
            strategy = CustomStrategyExecutor(config, cs_data)

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
        JSON string produced by :func:`~src.interfaces.workers.serializers.df_to_json`.

    Returns
    -------
    str
        :class:`~src.domain.intelligence.regime.MarketRegime` value string.
    """
    try:
        from src.domain.intelligence.regime import RegimeClassifier

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
    from src.infrastructure.database import MemgraphDatabase
    from src.domain.intelligence.news_ingestor import NewsIngestor
    from src.domain.intelligence.nlp import OllamaNLP
    from src.domain.intelligence.ai_service import AIService
    from src.domain.intelligence.aggregator import IntelligenceAggregator
    from src.interfaces.workers.serializers import serialize_event

    config = get_config()

    async def _run_pipeline():
        db = MemgraphDatabase(
            host=config.database.host,
            port=config.database.port,
            username=config.database.username,
            password=config.database.password,
            encrypted=config.database.encrypted,
        )
        await db.connect()

        api_key = config.graph.cryptocompare_api_key

        ingestor = NewsIngestor(db=db, cryptocompare_api_key=api_key)

        # Parallel ingest operations
        results = await asyncio.gather(
            ingestor.fetch_cryptocompare(),
            ingestor.fetch_rss_feeds(),
            ingestor.fetch_fear_greed(),
            ingestor.fetch_cv_news(),
            return_exceptions=True,
        )

        cryptocompare_events = results[0] if isinstance(results[0], list) else []
        rss_events = results[1] if isinstance(results[1], list) else []
        cv_events = results[3] if isinstance(results[3], list) else []

        all_new_events = cryptocompare_events + rss_events + cv_events

        nlp = OllamaNLP(
            base_url=config.intelligence.ollama_base_url,
            model=config.intelligence.ollama_model,
            timeout=int(config.intelligence.generation_timeout)
        )

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
            int(getattr(config.graph, "news_ttl_days", 7))
            if hasattr(config, "graph")
            else 7
        )
        await ingestor.prune_old_news(days=days_to_keep)

        await db.close()

        return {
            "cryptocompare_events": len(cryptocompare_events),
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


@celery_app.task(name="omnitrader.generate_ai_overview")
def generate_ai_overview():
    """Celery task to generate the periodic AI market overview."""
    import asyncio
    return asyncio.run(_generate_ai_overview_async())


async def _generate_ai_overview_async():
    """Async implementation of AI overview generation."""
    from src.config import get_config
    from src.domain.intelligence.aggregator import IntelligenceAggregator
    from src.domain.intelligence.ai_service import AIService
    from src.infrastructure.database.factory import DatabaseFactory
    from src.infrastructure.database.redis import get_redis_client

    config = get_config()
    db = DatabaseFactory.get_database(config)
    redis_client = get_redis_client()

    try:
        await db.connect()
        
        # Initialize services
        aggregator = IntelligenceAggregator(db=db, redis_client=redis_client)
        ai_service = AIService(
            base_url=config.intelligence.ollama_base_url,
            model=config.intelligence.ollama_model,
            timeout=config.intelligence.generation_timeout
        )
        
        # 1. Aggregate context
        logger.info("ai_overview_aggregating_context")
        context = await aggregator.aggregate_all()
        
        # 2. Generate summary
        logger.info("ai_overview_generating_summary")
        overview = await ai_service.generate_summary(context)
        
        # 3. Save results
        logger.info("ai_overview_saving_results")
        await ai_service.save_overview(overview, db, redis_client)
        
        return overview.model_dump()
    except Exception as e:
        logger.error("ai_overview_task_failed", error=str(e))
        raise
    finally:
        await db.close()


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
        from src.infrastructure.database import DatabaseFactory
        from src.domain.intelligence.analytics import GraphAnalytics

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
