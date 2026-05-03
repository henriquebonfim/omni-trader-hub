from dataclasses import dataclass
from datetime import UTC, datetime

import structlog

from src.domain.intelligence.regime import MarketRegime

ROTATION_COOLDOWN_HOURS = 4

logger = structlog.get_logger()


@dataclass
class StrategyScore:
    name: str
    sample_size: int
    sharpe: float
    profit_factor: float
    win_rate: float
    composite_score: float


class StrategySelector:
    """Selects the best strategy for a given market regime based on performance history."""

    def __init__(self, database):
        self.database = database
        self.min_sample_size = 20
        self.fallback_strategy = "adx_trend"
        self._last_rotation_at: datetime | None = None

    def can_rotate(self) -> bool:
        """Return True if enough time has passed since the last strategy rotation."""
        if self._last_rotation_at is None:
            return True
        elapsed = (datetime.now(UTC) - self._last_rotation_at).total_seconds()
        return elapsed >= ROTATION_COOLDOWN_HOURS * 3600

    def record_rotation(self) -> None:
        """Mark the current time as the last rotation timestamp."""
        self._last_rotation_at = datetime.now(UTC)

    async def get_strategy_performance(
        self, regime: MarketRegime
    ) -> list[StrategyScore]:
        """
        Query the database for strategy performance metrics filtered by regime.
        This queries closed trades linked via TRIGGERED_BY to signals.
        """
        # Memgraph doesn't have stDev, so we fetch raw pnl_pct list and gross profit/loss
        query = """
           MATCH (s:Signal {regime: $regime})<-[:TRIGGERED_BY]-(t_open:Trade {action: 'OPEN'})
           MATCH (t_close:Trade {action: 'CLOSE', symbol: t_open.symbol})
           WHERE t_close.timestamp > t_open.timestamp
           WITH s.strategy_name AS name, t_close
           ORDER BY t_close.timestamp ASC
           WITH name,
             count(t_close) AS total_trades,
             sum(CASE WHEN t_close.pnl > 0 THEN 1 ELSE 0 END) AS winning_trades,
             sum(CASE WHEN t_close.pnl > 0 THEN t_close.pnl ELSE 0 END) AS gross_profit,
             abs(sum(CASE WHEN t_close.pnl < 0 THEN t_close.pnl ELSE 0 END)) AS gross_loss,
             collect(t_close.pnl_pct) AS returns
           WHERE name IS NOT NULL AND name <> "" AND total_trades >= $min_sample

        RETURN name,
               total_trades as sample_size,
               winning_trades,
               gross_profit,
               gross_loss,
               returns
        """

        scores = []
        try:
            records = []
            if hasattr(self.database, "_driver"):
                async with self.database._driver.session() as session:
                    result = await session.run(
                        query, regime=regime.value, min_sample=self.min_sample_size
                    )
                    records = await result.data()
            elif hasattr(self.database, "execute_query"):
                records = await self.database.execute_query(
                    query, regime=regime.value, min_sample=self.min_sample_size
                )

            import math

            for r in records:
                name = r["name"]
                sample_size = r["sample_size"]
                winning_trades = r["winning_trades"]
                gross_profit = r["gross_profit"]
                gross_loss = r["gross_loss"]
                returns = r["returns"]

                # Calculate Win Rate
                win_rate = winning_trades / sample_size if sample_size > 0 else 0.0

                # Calculate Profit Factor
                profit_factor = (
                    gross_profit / gross_loss if gross_loss > 0 else gross_profit
                )

                # Calculate Sharpe (Python side)
                sharpe = 0.0
                if sample_size > 1:
                    avg_return = sum(returns) / sample_size
                    # Sample standard deviation
                    variance = (
                        sum((x - avg_return) ** 2 for x in returns) / (sample_size - 1)
                    )
                    std_return = math.sqrt(variance)
                    if std_return > 0:
                        # Annualized-style or just sample-based sharpe
                        sharpe = (avg_return * math.sqrt(sample_size)) / std_return

                # Normalize values for composite score
                norm_sharpe = min(
                    max(sharpe / 3.0, 0.0), 1.0
                )  # Assume 3.0 is excellent
                norm_pf = min(
                    max((profit_factor - 1.0) / 2.0, 0.0), 1.0
                )  # Assume 3.0 is excellent
                norm_wr = win_rate

                composite_score = (
                    (0.4 * norm_sharpe) + (0.3 * norm_pf) + (0.3 * norm_wr)
                )

                scores.append(
                    StrategyScore(
                        name=name,
                        sample_size=sample_size,
                        sharpe=sharpe,
                        profit_factor=profit_factor,
                        win_rate=win_rate,
                        composite_score=composite_score,
                    )
                )
        except Exception as e:
            logger.error(
                "failed_to_fetch_strategy_scores", error=str(e), regime=regime.value
            )

        # If we need custom strategies to "feed into score queries", let's ensure they are returned
        # even if they have 0 trades, so they appear in /api/strategies/performance
        scored_names = {s.name for s in scores}

        # Add custom strategies with 0 trades if they have affinity for this regime
        if hasattr(self.database, "list_custom_strategies"):
            try:
                custom_strats = await self.database.list_custom_strategies()
                for cs in custom_strats:
                    affinity = cs.get("regime_affinity", [])
                    if (not affinity or regime.value in affinity) and cs[
                        "name"
                    ] not in scored_names:
                        scores.append(
                            StrategyScore(
                                name=cs["name"],
                                sample_size=0,
                                sharpe=0.0,
                                profit_factor=0.0,
                                win_rate=0.0,
                                composite_score=0.0,
                            )
                        )
            except Exception as e:
                logger.error(
                    "failed_to_fetch_custom_strategies_for_scores", error=str(e)
                )

        return scores

    async def get_best_strategy(
        self, regime: MarketRegime, respect_cooldown: bool = True
    ) -> str:
        """Get the best strategy for the given regime, respecting rotation cooldown."""
        if respect_cooldown and not self.can_rotate():
            logger.debug(
                "strategy_rotation_cooldown_active",
                last_rotation=self._last_rotation_at,
            )
            return None  # Caller should keep current strategy
        scores = await self.get_strategy_performance(regime)
        if not scores:
            return self.fallback_strategy

        # Sort by composite score desc, tie-break by higher sample size
        scores.sort(key=lambda s: (s.composite_score, s.sample_size), reverse=True)
        return scores[0].name
