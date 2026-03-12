"""
Memgraph implementation of the database interface.
Unified graph database replacing PostgreSQL + Neo4j + QuestDB.

Node Labels:
  :Trade - Open/close events (action: OPEN/CLOSE)
  :DailySummary - Daily P&L aggregates (date: YYYY-MM-DD)
  :EquitySnapshot - Balance snapshots (timestamp: ms epoch)
  :Signal - Strategy signals (timestamp: ms epoch)
  :FundingPayment - Funding rate payments
  :State - Persistent key-value state (key: unique identifier)
  :Asset - Cryptocurrency asset (symbol, name, sector, exchange, market_cap_tier)
  :NewsEvent - News event (id, title, source, published_at, sentiment_score, impact_level, raw_text)
  :Sector - Industry sector (name)
  :MacroIndicator - Macroeconomic indicator (name, value, timestamp)
  :Candle - Price candle (symbol, timeframe, timestamp, open, high, low, close, volume)

Relationships:
  Not currently used for main data flow (denormalized for query performance)
  (:Trade)-[:TRIGGERED_BY]->(:Signal) - Added in Phase 2
  (:Signal)-[:GENERATED_BY]->(strategy) - Added in Phase 2
  (:NewsEvent)-[:IMPACTS {magnitude}]->(:Asset) - Added in Phase 2
  (:NewsEvent)-[:MENTIONS]->(:Sector) - Added in Phase 2
  (:Asset)-[:BELONGS_TO]->(:Sector) - Added in Phase 2
  (:Asset)-[:CORRELATES_WITH {coefficient}]->(:Asset) - Added in Phase 2
"""

import json
import time
from datetime import datetime, timezone
from typing import Optional

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

from .base import BaseDatabase

logger = structlog.get_logger()


class MemgraphDatabase(BaseDatabase):
    """
    Memgraph (graph database) implementation.
    Supports Bolt protocol via neo4j driver.
    """

    def __init__(
        self,
        host: str = "memgraph",
        port: int = 7687,
        username: Optional[str] = None,
        password: Optional[str] = None,
        encrypted: bool = False,
    ):
        """
        Initialize Memgraph connection parameters.

        Args:
            host: Memgraph host (default: docker service name)
            port: Bolt port (default: 7687)
            username: Auth username (optional)
            password: Auth password (optional)
            encrypted: Use SSL/TLS (default: False for local)
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encrypted = encrypted

        self._driver: Optional[AsyncDriver] = None
        self._connection_string = f"bolt://{host}:{port}"

    async def connect(self):
        """Initialize driver and create indexes."""
        try:
            # Create driver with async support
            if self.username and self.password:
                self._driver = AsyncGraphDatabase.driver(
                    self._connection_string,
                    auth=(self.username, self.password),
                    encrypted=self.encrypted,
                )
            else:
                self._driver = AsyncGraphDatabase.driver(
                    self._connection_string,
                    encrypted=self.encrypted,
                )

            # Test connection
            async with self._driver.session() as session:
                result = await session.run("RETURN 1 as connected")
                await result.consume()

            # Create indexes on startup
            await self._create_indexes()

            logger.info(
                "database_connected",
                type="memgraph",
                host=self.host,
                port=self.port,
            )
        except (DriverError, Neo4jError) as e:
            logger.error("database_connection_failed", error=str(e))
            raise

    async def close(self):
        """Close driver connection."""
        if self._driver:
            await self._driver.close()
            logger.info("database_closed", type="memgraph")

    async def _create_indexes(self):
        """Create indexes for query performance."""
        indexes = [
            "CREATE INDEX ON :Trade(timestamp);",
            "CREATE INDEX ON :Trade(symbol);",
            "CREATE INDEX ON :Signal(timestamp);",
            "CREATE INDEX ON :EquitySnapshot(timestamp);",
            "CREATE INDEX ON :DailySummary(date);",
            "CREATE INDEX ON :State(key);",
            "CREATE INDEX ON :FundingPayment(timestamp);",
            "CREATE INDEX ON :NewsEvent(published_at);",
            "CREATE INDEX ON :Candle(symbol, timeframe, timestamp);",
            "CREATE INDEX ON :MacroIndicator(name);",
            "CREATE INDEX ON :CustomStrategy(name);",
        ]

        async with self._driver.session() as session:
            for index_query in indexes:
                try:
                    await session.run(index_query)
                except Neo4jError as e:
                    # Index may already exist, ignore
                    if "already exists" not in str(e):
                        logger.warning(
                            "index_creation_warning", query=index_query, error=str(e)
                        )

    async def backup_db(self):
        """
        Create a backup of the database.

        For Memgraph community edition, this triggers snapshot creation.
        Returns the backup timestamp.
        """
        try:
            async with self._driver.session() as session:
                # Memgraph snapshot command
                result = await session.run("CREATE SNAPSHOT;")
                await result.single()
                timestamp = datetime.now(timezone.utc).isoformat()
                logger.info("database_backup_created", timestamp=timestamp)
                return timestamp
        except Neo4jError as e:
            logger.error("backup_failed", error=str(e))
            raise

    # ==================== TRADE LOGGING ====================

    async def log_trade_open(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
        reason: str = "signal",
        expected_price: Optional[float] = None,
        slippage: Optional[float] = None,
        fee: Optional[float] = None,
        fee_currency: Optional[str] = None,
    ) -> int:
        """Log a OPEN trade event."""
        timestamp = int(time.time() * 1000)  # ms epoch

        query = """
        CREATE (t:Trade {
            timestamp: $timestamp,
            symbol: $symbol,
            side: $side,
            action: 'OPEN',
            price: $price,
            size: $size,
            notional: $notional,
            stop_loss: $stop_loss,
            take_profit: $take_profit,
            reason: $reason,
            expected_price: $expected_price,
            slippage: $slippage,
            fee: $fee,
            fee_currency: $fee_currency
        })
        RETURN id(t) as trade_id
        """

        async with self._driver.session() as session:
            result = await session.run(
                query,
                timestamp=timestamp,
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                notional=notional,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=reason,
                expected_price=expected_price,
                slippage=slippage,
                fee=fee,
                fee_currency=fee_currency,
            )
            record = await result.single()
            trade_id = record["trade_id"] if record else 0
            logger.info(
                "trade_opened",
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                price=price,
            )
            return trade_id

    async def log_trade_close(
        self,
        symbol: str,
        side: str,
        price: float,
        size: float,
        notional: float,
        pnl: float,
        pnl_pct: float,
        reason: str = "signal",
        expected_price: Optional[float] = None,
        slippage: Optional[float] = None,
        fee: Optional[float] = None,
        fee_currency: Optional[str] = None,
    ) -> int:
        """Log a CLOSE trade event."""
        timestamp = int(time.time() * 1000)  # ms epoch

        query = """
        CREATE (t:Trade {
            timestamp: $timestamp,
            symbol: $symbol,
            side: $side,
            action: 'CLOSE',
            price: $price,
            size: $size,
            notional: $notional,
            pnl: $pnl,
            pnl_pct: $pnl_pct,
            reason: $reason,
            expected_price: $expected_price,
            slippage: $slippage,
            fee: $fee,
            fee_currency: $fee_currency
        })
        RETURN id(t) as trade_id
        """

        async with self._driver.session() as session:
            result = await session.run(
                query,
                timestamp=timestamp,
                symbol=symbol,
                side=side,
                price=price,
                size=size,
                notional=notional,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason=reason,
                expected_price=expected_price,
                slippage=slippage,
                fee=fee,
                fee_currency=fee_currency,
            )
            record = await result.single()
            trade_id = record["trade_id"] if record else 0
            logger.info(
                "trade_closed",
                trade_id=trade_id,
                symbol=symbol,
                side=side,
                pnl=pnl,
                pnl_pct=pnl_pct,
            )
            return trade_id

    async def get_open_trade_fee(self, symbol: str) -> float:
        """Get the fee of the most recent OPEN trade for a symbol."""
        query = """
        MATCH (t:Trade {symbol: $symbol, action: 'OPEN'})
        RETURN t.fee as fee
        ORDER BY t.timestamp DESC
        LIMIT 1
        """

        async with self._driver.session() as session:
            result = await session.run(query, symbol=symbol)
            record = await result.single()
            fee = record["fee"] if record and record["fee"] is not None else 0.0
            return fee

    # ==================== DAILY SUMMARY ====================

    async def save_daily_summary(
        self,
        date: str,
        starting_balance: float,
        ending_balance: float,
        pnl: float,
        pnl_pct: float,
        trades_count: int,
        wins: int,
        losses: int,
    ):
        """Save or update daily summary (date is unique key)."""
        query = """
        MERGE (d:DailySummary {date: $date})
        SET
            d.starting_balance = $starting_balance,
            d.ending_balance = $ending_balance,
            d.pnl = $pnl,
            d.pnl_pct = $pnl_pct,
            d.trades_count = $trades_count,
            d.wins = $wins,
            d.losses = $losses
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                date=date,
                starting_balance=starting_balance,
                ending_balance=ending_balance,
                pnl=pnl,
                pnl_pct=pnl_pct,
                trades_count=trades_count,
                wins=wins,
                losses=losses,
            )
            logger.info("daily_summary_saved", date=date, pnl=pnl)

    async def get_daily_summary(self, date: str) -> Optional[dict]:
        """Get daily summary for a specific date."""
        query = """
        MATCH (d:DailySummary {date: $date})
        RETURN
            d.date as date,
            d.starting_balance as starting_balance,
            d.ending_balance as ending_balance,
            d.pnl as pnl,
            d.pnl_pct as pnl_pct,
            d.trades_count as trades_count,
            d.wins as wins,
            d.losses as losses
        """

        async with self._driver.session() as session:
            result = await session.run(query, date=date)
            record = await result.single()

            if not record:
                return None

            return {
                "date": record["date"],
                "starting_balance": record["starting_balance"],
                "ending_balance": record["ending_balance"],
                "pnl": record["pnl"],
                "pnl_pct": record["pnl_pct"],
                "trades_count": record["trades_count"],
                "wins": record["wins"],
                "losses": record["losses"],
            }

    # ==================== TRADES ====================

    async def get_recent_trades(self, limit: int = 10) -> list:
        """Get recent trades across all symbols."""
        query = """
        MATCH (t:Trade)
        RETURN
            id(t) as id,
            t.timestamp as timestamp,
            t.symbol as symbol,
            t.side as side,
            t.action as action,
            t.price as price,
            t.expected_price as expected_price,
            t.slippage as slippage,
            t.size as size,
            t.notional as notional,
            t.pnl as pnl,
            t.pnl_pct as pnl_pct,
            t.reason as reason,
            t.fee as fee,
            t.stop_loss as stop_loss,
            t.take_profit as take_profit
        ORDER BY t.timestamp DESC
        LIMIT $limit
        """

        async with self._driver.session() as session:
            result = await session.run(query, limit=limit)
            records = await result.fetch(limit)

            trades = []
            for record in records:
                trade = {
                    "id": record["id"],
                    "timestamp": record["timestamp"],
                    "symbol": record["symbol"],
                    "side": record["side"],
                    "action": record["action"],
                    "price": record["price"],
                    "expected_price": record["expected_price"],
                    "slippage": record["slippage"],
                    "size": record["size"],
                    "notional": record["notional"],
                    "pnl": record["pnl"],
                    "pnl_pct": record["pnl_pct"],
                    "reason": record["reason"],
                    "fee": record["fee"],
                    "stop_loss": record["stop_loss"],
                    "take_profit": record["take_profit"],
                }
                trades.append(trade)

            return trades

    async def get_last_trade(self, symbol: str) -> Optional[dict]:
        """Get the most recent trade for a symbol."""
        query = """
        MATCH (t:Trade {symbol: $symbol})
        RETURN
            id(t) as id,
            t.timestamp as timestamp,
            t.symbol as symbol,
            t.side as side,
            t.action as action,
            t.price as price,
            t.size as size,
            t.notional as notional,
            t.pnl as pnl,
            t.pnl_pct as pnl_pct,
            t.reason as reason,
            t.fee as fee,
            t.stop_loss as stop_loss,
            t.take_profit as take_profit
        ORDER BY t.timestamp DESC
        LIMIT 1
        """

        async with self._driver.session() as session:
            result = await session.run(query, symbol=symbol)
            record = await result.single()

            if not record:
                return None

            return {
                "id": record["id"],
                "timestamp": record["timestamp"],
                "symbol": record["symbol"],
                "side": record["side"],
                "action": record["action"],
                "price": record["price"],
                "size": record["size"],
                "notional": record["notional"],
                "pnl": record["pnl"],
                "pnl_pct": record["pnl_pct"],
                "reason": record["reason"],
                "fee": record["fee"],
                "stop_loss": record["stop_loss"],
                "take_profit": record["take_profit"],
            }

    async def get_weekly_pnl(self, start_date: str) -> float:
        """
        Get total PnL for CLOSED trades since start_date (inclusive).

        Args:
            start_date: ISO date string (YYYY-MM-DD) or epoch ms

        Returns:
            Total PnL as float
        """
        # Convert ISO date to timestamp if needed
        if isinstance(start_date, str) and len(start_date) == 10:  # YYYY-MM-DD
            start_timestamp = int(
                datetime.fromisoformat(start_date)
                .replace(tzinfo=timezone.utc)
                .timestamp()
                * 1000
            )
        else:
            start_timestamp = int(start_date)

        query = """
        MATCH (t:Trade {action: 'CLOSE'})
        WHERE t.timestamp >= $start_timestamp
        RETURN coalesce(sum(t.pnl), 0.0) as total_pnl
        """

        async with self._driver.session() as session:
            result = await session.run(query, start_timestamp=start_timestamp)
            record = await result.single()
            total_pnl = record["total_pnl"] if record else 0.0
            return float(total_pnl)

    # ==================== EQUITY & SNAPSHOTS ====================

    async def log_equity_snapshot(self, balance: float) -> None:
        """Log current balance as an equity snapshot."""
        timestamp = int(time.time() * 1000)  # ms epoch

        query = """
        CREATE (e:EquitySnapshot {
            timestamp: $timestamp,
            balance: $balance
        })
        """

        async with self._driver.session() as session:
            await session.run(query, timestamp=timestamp, balance=balance)

    async def get_equity_snapshots(self, limit: int = 200) -> list:
        """Get recent equity snapshots."""
        query = """
        MATCH (e:EquitySnapshot)
        RETURN
            id(e) as id,
            e.timestamp as timestamp,
            e.balance as balance
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        async with self._driver.session() as session:
            result = await session.run(query, limit=limit)
            records = await result.fetch(limit)

            snapshots = []
            for record in records:
                snapshot = {
                    "id": record["id"],
                    "timestamp": record["timestamp"],
                    "balance": record["balance"],
                }
                snapshots.append(snapshot)

            return snapshots

    # ==================== SIGNALS ====================

    async def log_signal(
        self,
        symbol: str,
        price: float,
        signal: str,
        regime: str,
        reason: str,
        strategy_name: str,
        indicators: dict,
    ) -> None:
        """Log a strategy signal with indicator snapshot."""
        timestamp = int(time.time() * 1000)  # ms epoch

        query = """
        CREATE (s:Signal {
            timestamp: $timestamp,
            symbol: $symbol,
            price: $price,
            signal: $signal,
            regime: $regime,
            reason: $reason,
            strategy_name: $strategy_name,
            indicators: $indicators
        })
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                timestamp=timestamp,
                symbol=symbol,
                price=price,
                signal=signal,
                regime=regime,
                reason=reason,
                strategy_name=strategy_name,
                indicators=json.dumps(indicators),
            )
            logger.info(
                "signal_logged",
                symbol=symbol,
                signal=signal,
                regime=regime,
                price=price,
            )

    # ==================== FUNDING PAYMENTS ====================

    async def log_funding_payment(
        self,
        symbol: str,
        rate: float,
        payment: float,
        position_size: float,
    ) -> None:
        """Log a funding payment."""
        timestamp = int(time.time() * 1000)  # ms epoch

        query = """
        CREATE (f:FundingPayment {
            timestamp: $timestamp,
            symbol: $symbol,
            rate: $rate,
            payment: $payment,
            position_size: $position_size
        })
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                timestamp=timestamp,
                symbol=symbol,
                rate=rate,
                payment=payment,
                position_size=position_size,
            )
            logger.info(
                "funding_payment_logged",
                symbol=symbol,
                payment=payment,
                rate=rate,
            )

    # ==================== STATE PERSISTENCE ====================

    async def set_state(
        self, key: str, value: dict, expires_in: Optional[int] = None
    ) -> None:
        """
        Save persistent key-value state.

        Args:
            key: Unique state key
            value: JSON-serializable dict
            expires_in: Optional TTL in seconds
        """
        timestamp = int(time.time() * 1000)
        expires_at = None
        if expires_in:
            expires_at = timestamp + (expires_in * 1000)

        query = """
        MERGE (s:State {key: $key})
        SET
            s.value = $value,
            s.updated_at = $timestamp,
            s.expires_at = $expires_at
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                key=key,
                value=json.dumps(value),
                timestamp=timestamp,
                expires_at=expires_at,
            )
            logger.debug("state_saved", key=key)

    async def get_state(self, key: str) -> Optional[dict]:
        """
        Retrieve persistent state by key.

        Returns:
            State dict or None if not found/expired
        """
        query = """
        MATCH (s:State {key: $key})
        WHERE s.expires_at IS NULL OR s.expires_at > timestamp()
        RETURN s.value as value
        """

        async with self._driver.session() as session:
            result = await session.run(query, key=key)
            record = await result.single()

            if not record or not record["value"]:
                return None

            return json.loads(record["value"])

    async def delete_state(self, key: str) -> None:
        """Delete state key."""
        query = "MATCH (s:State {key: $key}) DELETE s"

        async with self._driver.session() as session:
            await session.run(query, key=key)
            logger.debug("state_deleted", key=key)

    # ==================== CANDLES ====================

    async def save_candles(
        self, symbol: str, timeframe: str, candles: list[dict]
    ) -> int:
        """
        Save a list of candles to the database.
        Candle dict format: {"timestamp": int, "open": float, "high": float, "low": float, "close": float, "volume": float}
        Returns the number of candles saved.
        """
        if not candles:
            return 0

        # Optimization: use UNWIND to insert in bulk
        query = """
        UNWIND $candles AS candle
        MERGE (c:Candle {symbol: $symbol, timeframe: $timeframe, timestamp: candle.timestamp})
        SET c.open = candle.open,
            c.high = candle.high,
            c.low = candle.low,
            c.close = candle.close,
            c.volume = candle.volume
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                symbol=symbol,
                timeframe=timeframe,
                candles=candles,
            )
            # Memgraph driver does not return 'nodes created' summary via `result.consume().counters` reliably,
            # so we just return the length of the list we provided.
            return len(candles)

    async def get_candles(
        self,
        symbol: str,
        timeframe: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        """
        Retrieve ordered candles from the database.
        """
        conditions = ["c.symbol = $symbol", "c.timeframe = $timeframe"]
        if start_time is not None:
            conditions.append("c.timestamp >= $start_time")
        if end_time is not None:
            conditions.append("c.timestamp <= $end_time")

        where_clause = " AND ".join(conditions)
        limit_clause = f" LIMIT {limit}" if limit else ""

        query = f"""
        MATCH (c:Candle)
        WHERE {where_clause}
        RETURN c.timestamp as timestamp,
               c.open as open,
               c.high as high,
               c.low as low,
               c.close as close,
               c.volume as volume
        ORDER BY c.timestamp ASC
        {limit_clause}
        """

        async with self._driver.session() as session:
            result = await session.run(
                query,
                symbol=symbol,
                timeframe=timeframe,
                start_time=start_time,
                end_time=end_time,
            )
            records = await result.fetch(1000000)  # arbitrary large number

            candles = []
            for record in records:
                candles.append(
                    {
                        "timestamp": record["timestamp"],
                        "open": record["open"],
                        "high": record["high"],
                        "low": record["low"],
                        "close": record["close"],
                        "volume": record["volume"],
                    }
                )

            return candles

    # ==================== CUSTOM STRATEGIES ====================

    async def save_custom_strategy(
        self,
        name: str,
        description: str,
        regime_affinity: list[str],
        entry_long_json: list[dict],
        entry_short_json: list[dict],
        exit_long_json: list[dict],
        exit_short_json: list[dict],
        indicators_json: list[dict],
        stop_loss_atr_mult: Optional[float] = None,
        take_profit_atr_mult: Optional[float] = None,
        min_bars_between_entries: int = 10,
    ) -> None:
        """Save a custom strategy."""
        timestamp = int(time.time() * 1000)

        query = """
        MERGE (c:CustomStrategy {name: $name})
        ON CREATE SET c.created_at = $timestamp
        SET c.description = $description,
            c.regime_affinity = $regime_affinity,
            c.entry_long_json = $entry_long_json,
            c.entry_short_json = $entry_short_json,
            c.exit_long_json = $exit_long_json,
            c.exit_short_json = $exit_short_json,
            c.indicators_json = $indicators_json,
            c.stop_loss_atr_mult = $stop_loss_atr_mult,
            c.take_profit_atr_mult = $take_profit_atr_mult,
            c.min_bars_between_entries = $min_bars_between_entries,
            c.updated_at = $timestamp
        """

        async with self._driver.session() as session:
            await session.run(
                query,
                name=name,
                description=description,
                regime_affinity=json.dumps(regime_affinity),
                entry_long_json=json.dumps(entry_long_json),
                entry_short_json=json.dumps(entry_short_json),
                exit_long_json=json.dumps(exit_long_json),
                exit_short_json=json.dumps(exit_short_json),
                indicators_json=json.dumps(indicators_json),
                stop_loss_atr_mult=stop_loss_atr_mult,
                take_profit_atr_mult=take_profit_atr_mult,
                min_bars_between_entries=min_bars_between_entries,
                timestamp=timestamp,
            )
            logger.info("custom_strategy_saved", name=name)

    async def get_custom_strategy(self, name: str) -> Optional[dict]:
        """Get a custom strategy by name."""
        query = """
        MATCH (c:CustomStrategy {name: $name})
        RETURN
            c.name as name,
            c.description as description,
            c.regime_affinity as regime_affinity,
            c.entry_long_json as entry_long_json,
            c.entry_short_json as entry_short_json,
            c.exit_long_json as exit_long_json,
            c.exit_short_json as exit_short_json,
            c.indicators_json as indicators_json,
            c.stop_loss_atr_mult as stop_loss_atr_mult,
            c.take_profit_atr_mult as take_profit_atr_mult,
            c.min_bars_between_entries as min_bars_between_entries,
            c.created_at as created_at,
            c.updated_at as updated_at
        """

        async with self._driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()

            if not record:
                return None

            return {
                "name": record["name"],
                "description": record["description"],
                "regime_affinity": json.loads(record["regime_affinity"] or "[]"),
                "entry_long_json": json.loads(record["entry_long_json"] or "[]"),
                "entry_short_json": json.loads(record["entry_short_json"] or "[]"),
                "exit_long_json": json.loads(record["exit_long_json"] or "[]"),
                "exit_short_json": json.loads(record["exit_short_json"] or "[]"),
                "indicators_json": json.loads(record["indicators_json"] or "[]"),
                "stop_loss_atr_mult": record["stop_loss_atr_mult"],
                "take_profit_atr_mult": record["take_profit_atr_mult"],
                "min_bars_between_entries": record["min_bars_between_entries"],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"],
            }

    async def list_custom_strategies(self) -> list[dict]:
        """List all custom strategies."""
        query = """
        MATCH (c:CustomStrategy)
        RETURN
            c.name as name,
            c.description as description,
            c.regime_affinity as regime_affinity,
            c.entry_long_json as entry_long_json,
            c.entry_short_json as entry_short_json,
            c.exit_long_json as exit_long_json,
            c.exit_short_json as exit_short_json,
            c.indicators_json as indicators_json,
            c.stop_loss_atr_mult as stop_loss_atr_mult,
            c.take_profit_atr_mult as take_profit_atr_mult,
            c.min_bars_between_entries as min_bars_between_entries,
            c.created_at as created_at,
            c.updated_at as updated_at
        ORDER BY c.name ASC
        """

        async with self._driver.session() as session:
            result = await session.run(query)
            records = await result.fetch(1000)

            strategies = []
            for record in records:
                strategies.append(
                    {
                        "name": record["name"],
                        "description": record["description"],
                        "regime_affinity": json.loads(
                            record["regime_affinity"] or "[]"
                        ),
                        "entry_long_json": json.loads(
                            record["entry_long_json"] or "[]"
                        ),
                        "entry_short_json": json.loads(
                            record["entry_short_json"] or "[]"
                        ),
                        "exit_long_json": json.loads(record["exit_long_json"] or "[]"),
                        "exit_short_json": json.loads(
                            record["exit_short_json"] or "[]"
                        ),
                        "indicators_json": json.loads(
                            record["indicators_json"] or "[]"
                        ),
                        "stop_loss_atr_mult": record["stop_loss_atr_mult"],
                        "take_profit_atr_mult": record["take_profit_atr_mult"],
                        "min_bars_between_entries": record["min_bars_between_entries"],
                        "created_at": record["created_at"],
                        "updated_at": record["updated_at"],
                    }
                )

            return strategies

    async def delete_custom_strategy(self, name: str) -> bool:
        """Delete a custom strategy by name. Returns True if deleted, False if not found."""
        query = """
        MATCH (c:CustomStrategy {name: $name})
        WITH c, c IS NOT NULL as existed
        DELETE c
        RETURN existed
        """

        async with self._driver.session() as session:
            result = await session.run(query, name=name)
            record = await result.single()
            if record and record["existed"]:
                logger.info("custom_strategy_deleted", name=name)
                return True
            return False
