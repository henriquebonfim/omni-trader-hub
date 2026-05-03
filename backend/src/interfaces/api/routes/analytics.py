from fastapi import APIRouter, Depends, Request, Query
from typing import Dict, Any, List
import numpy as np

from ..auth import verify_api_key
from ....services.analytics import PerformanceCalculator

router = APIRouter(tags=["analytics"], dependencies=[Depends(verify_api_key)])

@router.get("/stats")
async def get_performance_stats(request: Request):
    """
    Calculate and return performance metrics: Sharpe Ratio, Max Drawdown, Win Rate, etc.
    """
    bot = request.app.state.bot
    
    # 1. Fetch data
    # We fetch a larger window for accurate stats
    trades = await bot.database.get_recent_trades(limit=500)
    equity_snapshots = await bot.database.get_equity_snapshots(limit=1000)
    
    # 2. Extract values for calculator
    # PnL percentages for Sharpe
    pnl_pcts = [t["pnl_pct"] for t in trades if t["action"] == "CLOSE" and t["pnl_pct"] is not None]
    
    # Balance curve for Max Drawdown
    # Snapshots are in DESC order, need CHRONO order for MDD
    equity_curve = [s["balance"] for s in reversed(equity_snapshots)]
    
    # Profits and losses for Profit Factor
    profits = [t["pnl"] for t in trades if t["action"] == "CLOSE" and t["pnl"] > 0]
    losses = [t["pnl"] for t in trades if t["action"] == "CLOSE" and t["pnl"] < 0]
    
    # Win/Loss counts for Win Rate
    win_count = len(profits)
    loss_count = len(losses)
    
    # 3. Calculate metrics
    calc = PerformanceCalculator()
    
    sharpe = calc.calculate_sharpe_ratio(pnl_pcts)
    mdd = calc.calculate_max_drawdown(equity_curve)
    profit_factor = calc.calculate_profit_factor(profits, losses)
    win_rate = calc.calculate_win_rate(win_count, loss_count)
    
    return {
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown": round(mdd, 4),
        "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
        "win_rate": round(win_rate * 100, 2),
        "total_trades": win_count + loss_count,
        "sample_size": {
            "trades": len(trades),
            "snapshots": len(equity_snapshots)
        }
    }

@router.get("/correlation")
async def get_correlation_matrix(
    request: Request,
    window: int = Query(default=100, ge=10, le=500)
):
    """
    Calculate price correlation between active symbols.
    (This is a stub, will be fully implemented in a follow-up task AA-2.2)
    """
    # For now return a dummy matrix or a 404/501 if we want to be strict
    # But Task AA-1.2 says expose API, so I'll provide a placeholder
    return {
        "matrix": {},
        "symbols": [],
        "note": "Fully implemented in AA-2.2"
    }
