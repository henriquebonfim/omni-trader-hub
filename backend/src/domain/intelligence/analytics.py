from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

from src.infrastructure.database.memgraph import MemgraphDatabase

logger = structlog.get_logger()


class GraphAnalytics:
    """
    Graph Analytics module for extracting trading intelligence from Memgraph.
    Provides JSON-serializable queries for sentiment, crisis, divergence, and sector contagion.
    """

    def __init__(self, database: MemgraphDatabase):
        self.db = database

    async def get_asset_sentiment(
        self, symbol: str, hours_lookback: int = 24
    ) -> dict[str, Any]:
        """
        Calculates aggregate sentiment for a specific asset over a given lookback period.
        Assumes nodes: (:NewsEvent)-[:MENTIONS {sentiment: float}]->(:Asset {symbol: str})
        """
        cutoff_date = (
            datetime.now(UTC) - timedelta(hours=hours_lookback)
        ).isoformat()

        query = """
        MATCH (n:NewsEvent)-[r:IMPACTS]->(a:Asset {symbol: $symbol})
        WHERE n.published_at >= $cutoff_date
        RETURN
            avg(r.magnitude) as avg_sentiment,
            count(n) as mention_count,
            sum(CASE WHEN r.magnitude > 0 THEN 1 ELSE 0 END) as positive_mentions,
            sum(CASE WHEN r.magnitude < 0 THEN 1 ELSE 0 END) as negative_mentions
        """

        try:
            async with self.db._driver.session() as session:
                result = await session.run(
                    query, symbol=symbol, cutoff_date=cutoff_date
                )
                record = await result.single()

                if record:
                    return {
                        "avg_sentiment": float(record["avg_sentiment"] or 0.0),
                        "mention_count": int(record["mention_count"]),
                        "positive_mentions": int(record["positive_mentions"]),
                        "negative_mentions": int(record["negative_mentions"]),
                    }
                return {
                    "avg_sentiment": 0.0,
                    "mention_count": 0,
                    "positive_mentions": 0,
                    "negative_mentions": 0,
                }
        except Exception as e:
            logger.error("graph_analytics_sentiment_error", symbol=symbol, error=str(e))
            return {
                "avg_sentiment": 0.0,
                "mention_count": 0,
                "positive_mentions": 0,
                "negative_mentions": 0,
            }

    async def detect_sector_contagion(
        self, symbol: str, hours_lookback: int = 24
    ) -> dict[str, Any]:
        """
        Analyzes negative sentiment spread within the asset's sector.
        Assumes: (:Asset)-[:BELONGS_TO]->(:Sector) and (:NewsEvent)-[:MENTIONS]->(:Asset)
        """
        cutoff_date = (
            datetime.now(UTC) - timedelta(hours=hours_lookback)
        ).isoformat()

        query = """
        MATCH (target:Asset {symbol: $symbol})-[:BELONGS_TO]->(s:Sector)<-[:BELONGS_TO]-(peer:Asset)
        MATCH (n:NewsEvent)-[r:MENTIONS]->(peer)
        WHERE target <> peer AND n.published_at >= $cutoff_date AND r.sentiment < -0.3
        RETURN
            s.name as sector_name,
            count(distinct peer) as peers_in_distress,
            avg(r.sentiment) as sector_distress_level
        """

        try:
            async with self.db._driver.session() as session:
                result = await session.run(
                    query, symbol=symbol, cutoff_date=cutoff_date
                )
                record = await result.single()

                if record and record["sector_name"]:
                    return {
                        "contagion_risk": (
                            True if record["peers_in_distress"] > 2 else False
                        ),
                        "sector": record["sector_name"],
                        "peers_in_distress": int(record["peers_in_distress"]),
                        "sector_distress_level": float(
                            record["sector_distress_level"] or 0.0
                        ),
                    }
                return {
                    "contagion_risk": False,
                    "sector": None,
                    "peers_in_distress": 0,
                    "sector_distress_level": 0.0,
                }
        except Exception as e:
            logger.error("graph_analytics_contagion_error", symbol=symbol, error=str(e))
            return {
                "contagion_risk": False,
                "sector": None,
                "peers_in_distress": 0,
                "sector_distress_level": 0.0,
            }

    async def detect_sentiment_divergence(
        self, symbol: str, current_price: float, hours_lookback: int = 24
    ) -> dict[str, Any]:
        """
        Checks for divergence between price trend and news sentiment trend.
        Simplified version: returns sentiment metrics alongside price for upper-layer comparison.
        """
        sentiment_data = await self.get_asset_sentiment(symbol, hours_lookback)

        # Divergence logic (simplified heuristic)
        # E.g. highly negative sentiment but price is somehow pumping (or we just return the raw comparison data)
        divergence = False
        divergence_type = "none"

        if sentiment_data["mention_count"] >= 3:
            if sentiment_data["avg_sentiment"] < -0.5:
                # Need historical price to fully verify, but we can flag strong negative sentiment
                divergence = True
                divergence_type = "bearish_sentiment"
            elif sentiment_data["avg_sentiment"] > 0.5:
                divergence = True
                divergence_type = "bullish_sentiment"

        return {
            "divergence_detected": divergence,
            "divergence_type": divergence_type,
            "sentiment": sentiment_data["avg_sentiment"],
        }
