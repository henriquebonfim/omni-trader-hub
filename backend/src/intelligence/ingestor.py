"""
News Ingestor Service.

Ingests crypto news from CryptoPanic and various RSS feeds, evaluates
Fear & Greed Index, and stores the processed data as nodes and relationships in Memgraph.
"""

import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import feedparser
import httpx

from src.rate_limiter import LeakyBucketRateLimiter

logger = logging.getLogger(__name__)


class NewsIngestor:
    """
    Ingests news from multiple sources and stores them into Memgraph.
    """

    def __init__(self, db: Any, cryptopanic_api_key: Optional[str] = None):
        """
        Initialize the NewsIngestor.

        Args:
            db: The MemgraphDatabase instance.
            cryptopanic_api_key: The API key for CryptoPanic.
        """
        self.db = db
        self.cryptopanic_api_key = cryptopanic_api_key
        # Free tier is ~100 requests / day => ~4 requests/hour => ~1 request / 15 mins
        # Use a safe rate limit. Here, we specify 1 request every 60 seconds (60 requests per hour).
        # We might need to reduce polling frequency to fit inside 100/day.
        self.rate_limiter = LeakyBucketRateLimiter(
            capacity=100, refill_rate=0.001
        )  # ~86/day

    async def _fetch_url(
        self, url: str, params: Optional[Dict] = None
    ) -> Optional[httpx.Response]:
        """Fetch URL with basic error handling and rate limiting."""
        # Optional wait
        await self.rate_limiter.acquire()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                return response
            except httpx.RequestError as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return None

    def _generate_id(self, url: str, title: str) -> str:
        """Generate a deterministic 16-character hex ID based on url and title."""
        content = f"{url}{title}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()[:16]

    async def is_duplicate(self, event_id: str) -> bool:
        """Check if a NewsEvent node with the given ID already exists."""
        query = "MATCH (n:NewsEvent {id: $id}) RETURN n.id AS id"
        async with self.db._driver.session() as session:
            result = await session.run(query, id=event_id)
            records = [record async for record in result]
            return len(records) > 0

    async def fetch_cryptopanic(self) -> List[str]:
        """
        Fetch the latest news from CryptoPanic API.

        Returns:
            A list of new NewsEvent IDs that were inserted.
        """
        if not self.cryptopanic_api_key:
            logger.warning("No CryptoPanic API key configured. Skipping fetch.")
            return []

        url = "https://cryptopanic.com/api/v1/posts/"
        params = {"auth_token": self.cryptopanic_api_key, "public": "true"}

        response = await self._fetch_url(url, params)
        if not response:
            return []

        if asyncio.iscoroutine(response):
            response = await response

        data = response.json()
        new_event_ids = []

        for post in data.get("results", []):
            url_link = post.get("url", "")
            title = post.get("title", "")
            event_id = self._generate_id(url_link, title)

            if await self.is_duplicate(event_id):
                continue

            source = post.get("source", {}).get("domain", "CryptoPanic")
            published_at = post.get("published_at")
            vote_count = post.get("votes", {}).get("positive", 0) - post.get(
                "votes", {}
            ).get("negative", 0)

            # Simple fallback sentiment derived from votes
            sentiment_score = vote_count / max(abs(vote_count), 100)

            # Currencies mentioned
            currencies = [
                curr.get("code")
                for curr in post.get("currencies", [])
                if "code" in curr
            ]

            await self.create_news_event(
                event_id=event_id,
                title=title,
                url=url_link,
                source=source,
                published_at=published_at,
                sentiment_score=sentiment_score,
                raw_text=title,
                currencies=currencies,
            )
            new_event_ids.append(event_id)

        return new_event_ids

    async def fetch_fear_greed(self) -> None:
        """Fetch the current Fear & Greed Index value and store it as a MacroIndicator."""
        url = "https://api.alternative.me/fng/"
        response = await self._fetch_url(url)
        if not response:
            return

        if asyncio.iscoroutine(response):
            response = await response

        data = response.json()
        fng_data = data.get("data", [])
        if not fng_data:
            return

        current_fng = fng_data[0]
        value = int(current_fng.get("value", 50))
        # Alternative.me returns timestamp in seconds
        timestamp_sec = int(current_fng.get("timestamp", time.time()))

        # We store timestamp as ISO string or ms epoch. Let's use ms epoch to be consistent with others
        timestamp_ms = timestamp_sec * 1000

        query = """
        MERGE (m:MacroIndicator {name: 'Fear & Greed Index'})
        SET m.value = $value, m.timestamp = $timestamp
        """
        async with self.db._driver.session() as session:
            await session.run(query, value=value, timestamp=timestamp_ms)
            logger.info(f"Updated Fear & Greed Index: {value}")

    async def fetch_rss_feeds(self) -> List[str]:
        """
        Fetch news from popular crypto RSS feeds.

        Returns:
            A list of new NewsEvent IDs that were inserted.
        """
        feeds = [
            ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
            ("CoinTelegraph", "https://cointelegraph.com/rss"),
            ("The Block", "https://www.theblock.co/rss.xml"),
        ]

        new_event_ids = []

        # Run feed parsing in an executor to avoid blocking the event loop
        def _parse_feed(url):
            return feedparser.parse(url)

        for source_name, url in feeds:
            try:
                # Use default executor
                feed = await asyncio.get_event_loop().run_in_executor(
                    None, _parse_feed, url
                )

                for entry in feed.entries[:10]:  # Limit to 10 most recent per feed
                    link = entry.get("link", "")
                    title = entry.get("title", "")
                    event_id = self._generate_id(link, title)

                    if await self.is_duplicate(event_id):
                        continue

                    # Try to parse published date
                    published_parsed = entry.get("published_parsed")
                    if published_parsed:
                        # feedparser returns a time.struct_time
                        published_at = time.strftime(
                            "%Y-%m-%dT%H:%M:%S+00:00", published_parsed
                        )
                    else:
                        published_at = datetime.now(timezone.utc).isoformat()

                    summary = entry.get("summary", "")
                    # Combine title and summary for the raw text
                    raw_text = f"{title}. {summary}"

                    # Regex match basic tickers as a fallback before Ollama
                    tickers_found = re.findall(
                        r"\b(BTC|ETH|SOL|ADA|XRP|DOT|DOGE|AVAX|MATIC|LINK)\b", raw_text
                    )
                    currencies = list(set(tickers_found))

                    await self.create_news_event(
                        event_id=event_id,
                        title=title,
                        url=link,
                        source=source_name,
                        published_at=published_at,
                        sentiment_score=0.0,  # Default, Ollama will update
                        raw_text=raw_text,
                        currencies=currencies,
                    )
                    new_event_ids.append(event_id)
            except Exception as e:
                logger.error(f"Failed to process RSS feed {source_name}: {e}")

        return new_event_ids

    async def create_news_event(
        self,
        event_id: str,
        title: str,
        url: str,
        source: str,
        published_at: str,
        sentiment_score: float,
        raw_text: str,
        currencies: List[str],
    ):
        """Create a NewsEvent node and its relations in Memgraph."""
        query_node = """
        CREATE (n:NewsEvent {
            id: $id,
            title: $title,
            url: $url,
            source: $source,
            published_at: $published_at,
            sentiment_score: $sentiment_score,
            impact_level: 0.0,
            raw_text: $raw_text
        })
        """
        async with self.db._driver.session() as session:
            await session.run(
                query_node,
                id=event_id,
                title=title,
                url=url,
                source=source,
                published_at=published_at,
                sentiment_score=sentiment_score,
                raw_text=raw_text,
            )

            # Create basic relations for currencies if any
            for currency in currencies:
                query_rel = """
                MATCH (n:NewsEvent {id: $id})
                MERGE (a:Asset {symbol: $symbol})
                MERGE (n)-[:MENTIONS {sentiment: $sentiment}]->(a)
                """
                await session.run(
                    query_rel,
                    id=event_id,
                    symbol=currency.upper(),
                    sentiment=sentiment_score,
                )

        logger.info(f"Created NewsEvent: {event_id} from {source}")

    async def prune_old_news(self, days: int = 7):
        """Delete NewsEvent nodes older than `days` days."""
        # Calculate the cutoff date as ISO 8601 string
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        query = """
        MATCH (n:NewsEvent)
        WHERE n.published_at < $cutoff_date
        DETACH DELETE n
        RETURN count(n) as deleted_count
        """
        async with self.db._driver.session() as session:
            result = await session.run(query, cutoff_date=cutoff_date)
            records = [record async for record in result]
            if records:
                deleted_count = records[0]["deleted_count"]
                logger.info(f"Pruned {deleted_count} old NewsEvent nodes.")
