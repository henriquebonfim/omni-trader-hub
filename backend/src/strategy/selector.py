from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

import structlog

from src.intelligence.regime import MarketRegime

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
        elapsed = (datetime.now(timezone.utc) - self._last_rotation_at).total_seconds()
        return elapsed >= ROTATION_COOLDOWN_HOURS * 3600

    def record_rotation(self) -> None:
        """Mark the current time as the last rotation timestamp."""
        self._last_rotation_at = datetime.now(timezone.utc)

    async def get_strategy_performance(
        self, regime: MarketRegime
    ) -> List[StrategyScore]:
        """
        Query the database for strategy performance metrics filtered by regime.
        This queries trades linked to signals to calculate sharpe, profit_factor, and win_rate.
        """
        query = """
           MATCH (t:Trade {action: 'CLOSE'})
           MATCH (s:Signal {symbol: t.symbol, regime: $regime})
           WHERE s.timestamp <= t.timestamp AND s.strategy_name IS NOT NULL
           WITH t, s
           ORDER BY t.timestamp, s.timestamp DESC
           WITH t, head(collect(s)) AS latest_signal
           WITH latest_signal.strategy_name AS name,
             count(t) AS total_trades,
             sum(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) AS winning_trades,
             sum(CASE WHEN t.pnl > 0 THEN t.pnl ELSE 0 END) AS gross_profit,
             abs(sum(CASE WHEN t.pnl < 0 THEN t.pnl ELSE 0 END)) AS gross_loss,
             avg(t.pnl_pct) AS avg_return,
             stDev(t.pnl_pct) AS std_return
           WHERE name IS NOT NULL AND total_trades >= $min_sample

        RETURN name,
               total_trades as sample_size,
               CASE WHEN std_return > 0 THEN (avg_return * sqrt(total_trades)) / std_return ELSE 0.0 END AS sharpe,
               CASE WHEN gross_loss > 0 THEN gross_profit / gross_loss ELSE gross_profit END AS profit_factor,
               toFloat(winning_trades) / total_trades AS win_rate
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

            for r in records:
                sharpe = r["sharpe"] or 0.0
                profit_factor = r["profit_factor"] or 0.0
                win_rate = r["win_rate"] or 0.0

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
                        name=r["name"],
                        sample_size=r["sample_size"],
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
