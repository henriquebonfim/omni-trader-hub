import time
import os
from typing import Dict, Any

from fastapi import APIRouter, Request
import psutil

from ..schemas import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Simple cache for expensive metrics
_metrics_cache: Dict[str, Any] = {}
_metrics_cache_time: float = 0
CACHE_TTL = 5.0  # seconds

@router.get("", response_model=MetricsResponse)
async def get_metrics(request: Request):
    """
    Comprehensive runtime metrics including trade performance,
    system performance, exchange connectivity, and error rates.
    """
    global _metrics_cache, _metrics_cache_time
    
    current_time = time.time()
    if current_time - _metrics_cache_time < CACHE_TTL and _metrics_cache:
        return _metrics_cache

    manager = getattr(request.app.state, "bot_manager", None)
    bot = getattr(request.app.state, "bot", None)
    
    if manager and manager.bots:
        bot = manager.get_bot("default") or list(manager.bots.values())[0]

    # --- Trade Performance ---
    win_rate = 0.0
    total_pnl = 0.0
    total_volume = 0.0
    total_trades = 0
    
    if bot and bot.database:
        # Note: We aggregate over all time or daily, depending on DB support.
        # For simplicity we might just pull daily stats or last N trades if direct query not available.
        # Let's try to get daily stats as a proxy if full aggregations aren't easily available
        try:
            if bot.risk:
                daily_stats = bot.risk.get_daily_stats()
                if daily_stats:
                    win_rate = daily_stats.win_rate
                    total_pnl = daily_stats.realized_pnl
                    total_trades = daily_stats.trades_count
                    # Volume might not be in daily_stats directly, but we do our best
        except Exception:
            pass

    # --- System Performance ---
    process = psutil.Process(os.getpid())
    cpu_usage_pct = process.cpu_percent(interval=None) # Non-blocking
    mem_info = process.memory_info()
    memory_usage_mb = mem_info.rss / (1024 * 1024)
    memory_usage_pct = process.memory_percent()

    # --- Exchange Connectivity ---
    exchange_status = "unknown"
    exchange_latency_ms = 0.0
    
    if bot and bot.exchange:
        try:
            start_ping = time.perf_counter()
            # A simple lightweight call to check latency
            await bot.exchange.get_ticker(bot.config.trading.symbol)
            exchange_latency_ms = (time.perf_counter() - start_ping) * 1000
            exchange_status = "connected"
        except Exception:
            exchange_status = "disconnected"

    # --- Error Rates / Logs ---
    # We will need a way to track errors. If not built-in, we default to 0 and assume we might track it in memory.
    error_count = getattr(request.app.state, "error_count", 0)

    # --- Queue Depths ---
    # If using Celery, we can inspect queues. For now, mock or return empty if not directly accessible via bot
    queue_depths = {}
    
    response_data = {
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "total_volume": total_volume,
        "total_trades": total_trades,
        "cpu_usage_pct": round(cpu_usage_pct, 2),
        "memory_usage_mb": round(memory_usage_mb, 2),
        "memory_usage_pct": round(memory_usage_pct, 2),
        "exchange_status": exchange_status,
        "exchange_latency_ms": round(exchange_latency_ms, 2),
        "error_count": error_count,
        "queue_depths": queue_depths,
    }
    
    _metrics_cache = response_data
    _metrics_cache_time = current_time
    
    return response_data
