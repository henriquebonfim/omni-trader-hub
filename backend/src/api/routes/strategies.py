"""
Strategy listing route.
"""

from typing import Any, Dict, List, Optional

import talib
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.api.auth import verify_api_key
from src.intelligence.regime import MarketRegime
from src.strategy.registry import get_all_strategies, get_strategy

router = APIRouter(tags=["strategies"])

class IndicatorConfig(BaseModel):
    function: str
    params: Dict[str, Any]
    output_name: str

class ConditionConfig(BaseModel):
    indicator: str
    operator: str
    value: Any

class CustomStrategyCreate(BaseModel):
    name: str
    description: str = ""
    regime_affinity: List[str] = []
    entry_long_json: List[ConditionConfig] = []
    entry_short_json: List[ConditionConfig] = []
    exit_long_json: List[ConditionConfig] = []
    exit_short_json: List[ConditionConfig] = []
    indicators_json: List[IndicatorConfig] = []
    stop_loss_atr_mult: Optional[float] = None
    take_profit_atr_mult: Optional[float] = None
    min_bars_between_entries: int = 10


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
    """List all registered strategies (built-in + custom)."""
    bot = request.app.state.bot
    active = getattr(bot.config.strategy, "name", "ema_volume")

    strategies = []
    
    # Built-in strategies
    for name, cls in get_all_strategies().items():
        try:
            # Instantiate temporarily to read metadata
            instance = cls(bot.config)
            meta = instance.metadata
            regimes = [r.value for r in instance.valid_regimes]
        except Exception:
            meta = {}
            regimes = []
            
        strategies.append(
            {
                "name": name,
                "type": "built-in",
                "description": meta.get("description", ""),
                "regime_affinity": regimes,
                "editable": False,
                "active": name == active,
            }
        )

    # Custom strategies
    if hasattr(bot.database, "list_custom_strategies"):
        custom_strats = await bot.database.list_custom_strategies()
        for cs in custom_strats:
            strategies.append(
                {
                    "name": cs["name"],
                    "type": "custom",
                    "description": cs.get("description", ""),
                    "regime_affinity": cs.get("regime_affinity", []),
                    "conditions": {
                        "entry_long": cs.get("entry_long_json", []),
                        "entry_short": cs.get("entry_short_json", []),
                        "exit_long": cs.get("exit_long_json", []),
                        "exit_short": cs.get("exit_short_json", []),
                    },
                    "indicators": cs.get("indicators_json", []),
                    "editable": True,
                    "active": cs["name"] == active,
                }
            )

    return {"strategies": strategies, "active": active}


def validate_custom_strategy(strat: CustomStrategyCreate):
    """Validate strategy configuration."""
    valid_operators = {">", "<", ">=", "<=", "crosses_above", "crosses_below"}
    indicator_outputs = {ind.output_name for ind in strat.indicators_json}
    indicator_outputs.update({"close", "open", "high", "low", "volume"})

    # Check talib functions
    for ind in strat.indicators_json:
        try:
            talib.abstract.Function(ind.function)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid TA-Lib function: {ind.function}") from e

    # Check conditions
    all_conditions = (
        strat.entry_long_json + strat.entry_short_json +
        strat.exit_long_json + strat.exit_short_json
    )
    for cond in all_conditions:
        if cond.operator not in valid_operators:
            raise HTTPException(status_code=400, detail=f"Invalid operator: {cond.operator}")
        if cond.indicator not in indicator_outputs:
            raise HTTPException(status_code=400, detail=f"Condition references unknown indicator: {cond.indicator}")
        if isinstance(cond.value, str) and cond.value not in indicator_outputs:
            try:
                float(cond.value)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Condition value must be number or valid indicator, got: {cond.value}") from e


@router.get("/strategies/{name}")
async def get_strategy_detail(request: Request, name: str):
    bot = request.app.state.bot

    # Check built-in
    try:
        cls = get_strategy(name)
        instance = cls(bot.config)
        return {
            "name": name,
            "type": "built-in",
            "description": instance.metadata.get("description", ""),
            "regime_affinity": [r.value for r in instance.valid_regimes],
            "editable": False,
        }
    except ValueError:
        pass

    # Check custom
    if hasattr(bot.database, "get_custom_strategy"):
        cs = await bot.database.get_custom_strategy(name)
        if cs:
            return {
                "name": cs["name"],
                "type": "custom",
                "description": cs.get("description", ""),
                "regime_affinity": cs.get("regime_affinity", []),
                "conditions": {
                    "entry_long": cs.get("entry_long_json", []),
                    "entry_short": cs.get("entry_short_json", []),
                    "exit_long": cs.get("exit_long_json", []),
                    "exit_short": cs.get("exit_short_json", []),
                },
                "indicators": cs.get("indicators_json", []),
                "stop_loss_atr_mult": cs.get("stop_loss_atr_mult"),
                "take_profit_atr_mult": cs.get("take_profit_atr_mult"),
                "min_bars_between_entries": cs.get("min_bars_between_entries", 10),
                "editable": True,
            }

    raise HTTPException(status_code=404, detail="Strategy not found")


@router.post("/strategies")
async def create_custom_strategy(
    request: Request,
    strat: CustomStrategyCreate,
    _: str = Depends(verify_api_key)
):
    bot = request.app.state.bot

    # Check if name is taken by built-in
    try:
        get_strategy(strat.name)
        raise HTTPException(status_code=400, detail="Name conflicts with built-in strategy")
    except ValueError:
        pass

    # Check if name already exists in custom
    if hasattr(bot.database, "get_custom_strategy"):
        existing = await bot.database.get_custom_strategy(strat.name)
        if existing:
            raise HTTPException(status_code=400, detail="Custom strategy with this name already exists")

    validate_custom_strategy(strat)

    await bot.database.save_custom_strategy(
        name=strat.name,
        description=strat.description,
        regime_affinity=strat.regime_affinity,
        entry_long_json=[c.model_dump() for c in strat.entry_long_json],
        entry_short_json=[c.model_dump() for c in strat.entry_short_json],
        exit_long_json=[c.model_dump() for c in strat.exit_long_json],
        exit_short_json=[c.model_dump() for c in strat.exit_short_json],
        indicators_json=[i.model_dump() for i in strat.indicators_json],
        stop_loss_atr_mult=strat.stop_loss_atr_mult,
        take_profit_atr_mult=strat.take_profit_atr_mult,
        min_bars_between_entries=strat.min_bars_between_entries,
    )
    return {"status": "success", "name": strat.name}


@router.put("/strategies/{name}")
async def update_custom_strategy(
    request: Request,
    name: str,
    strat: CustomStrategyCreate,
    _: str = Depends(verify_api_key)
):
    bot = request.app.state.bot

    # Enforce name match
    if strat.name != name:
        raise HTTPException(status_code=400, detail="Path name and body name must match")

    # Ensure it exists as a custom strategy
    existing = await bot.database.get_custom_strategy(name)
    if not existing:
        raise HTTPException(status_code=404, detail="Custom strategy not found")

    validate_custom_strategy(strat)

    await bot.database.save_custom_strategy(
        name=strat.name,
        description=strat.description,
        regime_affinity=strat.regime_affinity,
        entry_long_json=[c.model_dump() for c in strat.entry_long_json],
        entry_short_json=[c.model_dump() for c in strat.entry_short_json],
        exit_long_json=[c.model_dump() for c in strat.exit_long_json],
        exit_short_json=[c.model_dump() for c in strat.exit_short_json],
        indicators_json=[i.model_dump() for i in strat.indicators_json],
        stop_loss_atr_mult=strat.stop_loss_atr_mult,
        take_profit_atr_mult=strat.take_profit_atr_mult,
        min_bars_between_entries=strat.min_bars_between_entries,
    )
    return {"status": "success", "name": strat.name}


@router.delete("/strategies/{name}")
async def delete_custom_strategy(
    request: Request,
    name: str,
    _: str = Depends(verify_api_key)
):
    bot = request.app.state.bot

    # Cannot delete built-in
    try:
        get_strategy(name)
        raise HTTPException(status_code=404, detail="Strategy not found") # Or 400? Prompt asks for 404 for built-in strategy deletion
    except ValueError:
        pass

    if hasattr(bot.database, "delete_custom_strategy"):
        deleted = await bot.database.delete_custom_strategy(name)
        if deleted:
            return {"status": "success", "name": name}

    raise HTTPException(status_code=404, detail="Custom strategy not found")
