import structlog
from typing import List
from dataclasses import dataclass
from src.intelligence.regime import MarketRegime

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

    async def get_strategy_performance(self, regime: MarketRegime) -> List[StrategyScore]:
        """
        Query the database for strategy performance metrics filtered by regime.
        This queries trades linked to signals to calculate sharpe, profit_factor, and win_rate.
        """
        # We need a query that aggregates performance per strategy for the given regime.
        query = """
        MATCH (t:Trade)-[:TRIGGERED_BY]->(s:Signal)
        WHERE s.regime = $regime AND t.status = 'closed'
        WITH s.strategy_name AS name,
             count(t) AS total_trades,
             sum(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) AS winning_trades,
             sum(CASE WHEN t.pnl > 0 THEN t.pnl ELSE 0 END) AS gross_profit,
             abs(sum(CASE WHEN t.pnl < 0 THEN t.pnl ELSE 0 END)) AS gross_loss,
             avg(t.pnl_pct) AS avg_return,
             stDev(t.pnl_pct) AS std_return
        
        WHERE total_trades >= $min_sample
        
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
                        query, 
                        regime=regime.value, 
                        min_sample=self.min_sample_size
                    )
                    records = await result.data()
            elif hasattr(self.database, "execute_query"):
                records = await self.database.execute_query(
                    query, 
                    regime=regime.value, 
                    min_sample=self.min_sample_size
                )
                
            for r in records:
                sharpe = r["sharpe"] or 0.0
                profit_factor = r["profit_factor"] or 0.0
                win_rate = r["win_rate"] or 0.0
                
                # Normalize values for composite score
                norm_sharpe = min(max(sharpe / 3.0, 0.0), 1.0) # Assume 3.0 is excellent
                norm_pf = min(max((profit_factor - 1.0) / 2.0, 0.0), 1.0) # Assume 3.0 is excellent
                norm_wr = win_rate
                
                composite_score = (0.4 * norm_sharpe) + (0.3 * norm_pf) + (0.3 * norm_wr)
                
                scores.append(StrategyScore(
                    name=r["name"],
                    sample_size=r["sample_size"],
                    sharpe=sharpe,
                    profit_factor=profit_factor,
                    win_rate=win_rate,
                    composite_score=composite_score
                ))
        except Exception as e:
            logger.error("failed_to_fetch_strategy_scores", error=str(e), regime=regime.value)
            
        return scores
        
    async def get_best_strategy(self, regime: MarketRegime) -> str:
        """Get the best strategy for the given regime."""
        scores = await self.get_strategy_performance(regime)
        if not scores:
            return self.fallback_strategy
            
        # Sort by composite score desc, tie-break by higher sample size
        scores.sort(key=lambda s: (s.composite_score, s.sample_size), reverse=True)
        return scores[0].name
