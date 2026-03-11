"""
Strategy listing route.
"""

from fastapi import APIRouter, Request

from src.strategy.registry import get_all_strategies
from src.intelligence.regime import MarketRegime

router = APIRouter(tags=["strategies"])


@router.get("/strategies/performance")
async def get_strategies_performance(request: Request):
    """Get grouped strategy scores by regime."""
    bot = request.app.state.bot
    if not hasattr(bot, "strategy_selector"):
        from src.strategy.selector import StrategySelector
        selector = StrategySelector(database=bot.database)
    else:
        selector = bot.strategy_selector
        
    results = {}
    for regime in MarketRegime:
        scores = await selector.get_strategy_performance(regime)
        results[regime.value] = [
            {
                "name": s.name,
                "sample_size": s.sample_size,
                "sharpe": s.sharpe,
                "profit_factor": s.profit_factor,
                "win_rate": s.win_rate,
                "composite_score": s.composite_score
            }
            for s in scores
        ]
        
    return {"performance": results}


@router.get("/strategies")
async def list_strategies(request: Request):
    """List all registered strategies with metadata."""
    bot = request.app.state.bot
    active = getattr(bot.config.strategy, "name", "ema_volume")

    strategies = []
    for name, cls in get_all_strategies().items():
        try:
            # Instantiate temporarily to read metadata
            instance = cls(bot.config)
            meta = instance.metadata
        except Exception:
            meta = {}
        strategies.append(
            {
                "name": name,
                "active": name == active,
                "metadata": meta,
            }
        )

    return {"strategies": strategies, "active": active}
