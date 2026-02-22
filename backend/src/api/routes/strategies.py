"""
Strategy listing route.
"""

from fastapi import APIRouter, Request

from src.strategies.registry import _STRATEGIES

router = APIRouter(tags=["strategies"])


@router.get("/strategies")
async def list_strategies(request: Request):
    """List all registered strategies with metadata."""
    bot = request.app.state.bot
    active = getattr(bot.config.strategy, "name", "ema_volume")

    strategies = []
    for name, cls in _STRATEGIES.items():
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
