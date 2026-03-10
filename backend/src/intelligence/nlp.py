"""
Ollama NLP Integration for Entity Extraction.

Extracts assets, sectors, sentiment, and impact from crypto news text using Ollama.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class OllamaNLP:
    """
    Ollama integration for NLP entity extraction from news events.
    """

    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llama3:8b", timeout: int = 30, redis_client: Optional[Any] = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.redis_client = redis_client
        # Using a single AsyncClient instance with connection pooling
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))

    async def close(self):
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def extract_entities(self, news_text: str) -> Dict[str, Any]:
        """
        Extract entities (assets, sectors, sentiment, impact) from text using Ollama.

        Args:
            news_text: The raw text of the news event.

        Returns:
            A dictionary containing 'assets', 'sectors', 'sentiment', and 'impact'.
        """
        prompt = f"""
Extract from this crypto news: "{news_text}"

Return JSON only (no markdown, no explanation):
{{
  "assets": ["BTC", "ETH"],
  "sectors": ["DeFi", "L1"],
  "sentiment": 0.7,
  "impact": 0.85
}}

Rules:
- sentiment: -1 (very negative) to +1 (very positive)
- impact: 0 (low) to 1 (critical crisis)
- assets: ticker symbols only (uppercase)
- sectors: DeFi, L1, L2, NFT, Gaming, Lending, DEX, Stablecoins, Infrastructure, Regulation
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            response = await self.client.post(f"{self.base_url}/api/generate", json=payload)
            if asyncio.iscoroutine(response):
                response = await response

            response.raise_for_status()
            data = response.json()
            if asyncio.iscoroutine(data):
                data = await data
            
            # Parse the response JSON string returned by Ollama
            response_text = data.get("response", "{}")
            result = json.loads(response_text)
            
            # Validation
            assets = result.get("assets", [])
            sectors = result.get("sectors", [])
            sentiment = float(result.get("sentiment", 0.0))
            impact = float(result.get("impact", 0.0))

            # Clamp values
            sentiment = max(-1.0, min(1.0, sentiment))
            impact = max(0.0, min(1.0, impact))
            
            await self._record_metric(success=True)
            
            return {
                "assets": [str(a).upper() for a in assets],
                "sectors": [str(s) for s in sectors],
                "sentiment": sentiment,
                "impact": impact
            }

        except (httpx.RequestError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Ollama entity extraction failed: {e}. Falling back to default.")
            await self._record_metric(success=False)
            return {}

    async def _record_metric(self, success: bool):
        """Record success or failure to Redis and alert if failure rate is too high (>50% over last hour)."""
        if not self.redis_client:
            return

        try:
            import time
            current_hour = int(time.time() / 3600)
            
            success_key = f"omnitrader:ollama:success:{current_hour}"
            fail_key = f"omnitrader:ollama:failure:{current_hour}"

            if success:
                self.redis_client.incr(success_key)
                self.redis_client.expire(success_key, 7200) # Expire in 2 hours
            else:
                fails = self.redis_client.incr(fail_key)
                self.redis_client.expire(fail_key, 7200)

                # Fetch successes
                successes = self.redis_client.get(success_key)
                successes = int(successes) if successes else 0
                
                total = successes + fails
                if total >= 10 and (fails / total) > 0.5:
                    logger.error(f"OLLAMA FAILURE ALERT: Failure rate is {fails/total:.1%} in the current hour ({fails}/{total}).")
        except Exception as e:
            logger.warning(f"Failed to record Ollama metrics: {e}")

    async def enrich_news_event(self, event_id: str, db: Any):
        """
        Fetch a news event from Memgraph, extract entities using Ollama,
        and update the event along with creating corresponding relationships.

        Args:
            event_id: The ID of the NewsEvent node.
            db: The MemgraphDatabase instance.
        """
        query_fetch = "MATCH (n:NewsEvent {id: $event_id}) RETURN n.raw_text AS raw_text, n.sentiment_score AS fallback_sentiment"
        
        async with db._driver.session() as session:
            result = await session.run(query_fetch, event_id=event_id)
            records = [record async for record in result]
            if not records:
                logger.error(f"NewsEvent with id {event_id} not found.")
                return
            record = records[0]

            raw_text = record["raw_text"]
            fallback_sentiment = record["fallback_sentiment"]

            entities = await self.extract_entities(raw_text)
            
            if not entities:
                logger.info(f"Using fallback sentiment for {event_id}")
                # Degraded mode: fallback to the existing sentiment derived from vote_count
                sentiment = fallback_sentiment
                impact = 0.5  # Default impact
                assets = []
                sectors = []
            else:
                sentiment = entities["sentiment"]
                impact = entities["impact"]
                assets = entities["assets"]
                sectors = entities["sectors"]

            # Update NewsEvent node
            query_update = """
            MATCH (n:NewsEvent {id: $event_id})
            SET n.sentiment_score = $sentiment, n.impact_level = $impact
            """
            await session.run(query_update, event_id=event_id, sentiment=sentiment, impact=impact)

            # Create Asset nodes and IMPACTS relationships
            for asset in assets:
                query_asset = """
                MATCH (n:NewsEvent {id: $event_id})
                MERGE (a:Asset {symbol: $symbol})
                MERGE (n)-[:IMPACTS {magnitude: $impact}]->(a)
                """
                await session.run(query_asset, event_id=event_id, symbol=asset, impact=impact)

            # Create Sector nodes and MENTIONS relationships
            for sector in sectors:
                query_sector = """
                MATCH (n:NewsEvent {id: $event_id})
                MERGE (s:Sector {name: $name})
                MERGE (n)-[:MENTIONS]->(s)
                """
                await session.run(query_sector, event_id=event_id, name=sector)

            logger.info(f"Enriched NewsEvent {event_id} with entities.")
