from datetime import UTC, datetime, timedelta
from typing import Any, List, Dict
import json
import structlog

from src.infrastructure.database.memgraph import MemgraphDatabase

logger = structlog.get_logger()

class IntelligenceAggregator:
    """
    Aggregates data from Redis (risk/PnL) and Memgraph (news/macro) 
    to provide context for AI intelligence generation.
    """

    def __init__(self, db: MemgraphDatabase, redis_client: Any):
        self.db = db
        self.redis = redis_client

    async def get_risk_context(self, bot_id: str = "default") -> Dict[str, Any]:
        """Fetch current risk and PnL state from Redis."""
        prefix = f"omnitrader:risk:{bot_id}:"
        try:
            # Daily Stats
            stats_raw = self.redis.get(f"{prefix}daily_stats")
            stats = json.loads(stats_raw) if stats_raw else {}

            # Circuit Breaker
            cb_raw = self.redis.get(f"{prefix}circuit_breaker")
            cb_active = json.loads(cb_raw).get("value", False) if cb_raw else False

            # Peak Equity
            peak_raw = self.redis.get(f"{prefix}peak_equity")
            peak_equity = json.loads(peak_raw).get("value", 0.0) if peak_raw else 0.0

            return {
                "realized_pnl": stats.get("realized_pnl", 0.0),
                "trades_count": stats.get("trades_count", 0),
                "win_rate": (stats.get("wins", 0) / stats.get("trades_count", 1)) if stats.get("trades_count", 0) > 0 else 0.0,
                "circuit_breaker_active": cb_active,
                "peak_equity": peak_equity,
                "drawdown": (peak_equity - stats.get("starting_balance", peak_equity)) / max(peak_equity, 1.0) if peak_equity > 0 else 0.0
            }
        except Exception as e:
            logger.error("aggregator_risk_context_error", error=str(e))
            return {}

    async def get_news_context(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch recent news events from Memgraph."""
        cutoff_date = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
        
        query = """
        MATCH (n:NewsEvent)
        WHERE n.published_at >= $cutoff_date
        RETURN n.title AS title, n.sentiment_score AS sentiment, n.impact_level AS impact, n.source AS source, n.published_at AS published_at
        ORDER BY n.published_at DESC
        LIMIT 20
        """
        
        try:
            async with self.db._driver.session() as session:
                result = await session.run(query, cutoff_date=cutoff_date)
                return [
                    {
                        "title": record["title"],
                        "sentiment": record["sentiment"],
                        "impact": record["impact"],
                        "source": record["source"],
                        "published_at": record["published_at"]
                    }
                    for record in [record async for record in result]
                ]
        except Exception as e:
            logger.error("aggregator_news_context_error", error=str(e))
            return []

    async def get_macro_context(self) -> Dict[str, Any]:
        """Fetch macro indicators like Fear & Greed Index."""
        query = """
        MATCH (m:MacroIndicator {name: 'Fear & Greed Index'})
        RETURN m.value AS value, m.timestamp AS timestamp
        """
        
        try:
            async with self.db._driver.session() as session:
                result = await session.run(query)
                record = await result.single()
                if record:
                    return {
                        "fear_and_greed": record["value"],
                        "timestamp": record["timestamp"]
                    }
                return {"fear_and_greed": 50}
        except Exception as e:
            logger.error("aggregator_macro_context_error", error=str(e))
            return {"fear_and_greed": 50}

    async def aggregate_all(self, bot_id: str = "default") -> Dict[str, Any]:
        """Get all context in one call."""
        risk = await self.get_risk_context(bot_id)
        news = await self.get_news_context()
        macro = await self.get_macro_context()
        
        return {
            "risk": risk,
            "news": news,
            "macro": macro,
            "timestamp": int(datetime.now(UTC).timestamp())
        }
