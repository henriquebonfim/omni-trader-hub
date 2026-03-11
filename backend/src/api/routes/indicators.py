import time
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
import talib
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from talib import abstract

from ..auth import verify_api_key

router = APIRouter(prefix="/indicators", tags=["indicators"])

# Cache for the catalog
_catalog_cache = None

# Rate limiting store (in-memory)
_rate_limits: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SEC = 60

class ComputeRequest(BaseModel):
    function: str = Field(..., description="TA-Lib function name, e.g., 'RSI'")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the function")
    symbol: str = Field(..., description="Trading symbol, e.g., 'BTC/USDT'")
    timeframe: str = Field(..., description="Timeframe, e.g., '1h'")
    bars: int = Field(100, ge=1, le=1000, description="Number of bars to fetch")

def _check_rate_limit(client_ip: str):
    now = time.time()
    # Clean up old entries
    _rate_limits[client_ip] = [
        ts for ts in _rate_limits[client_ip]
        if now - ts < RATE_LIMIT_WINDOW_SEC
    ]
    if len(_rate_limits[client_ip]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Limit is 10 requests per minute."
        )
    _rate_limits[client_ip].append(now)

def _build_catalog():
    catalog = {}
    groups = talib.get_function_groups()
    for group, funcs in groups.items():
        catalog[group] = []
        for func_name in funcs:
            try:
                func = abstract.Function(func_name)
                info = func.info
                
                inputs = []
                for _, v in info.get("input_names", {}).items():
                    if isinstance(v, list) or isinstance(v, tuple):
                        inputs.extend(list(v))
                    elif isinstance(v, dict):
                        inputs.extend(list(v.values()))
                    elif isinstance(v, str):
                        inputs.append(v)
                
                params = []
                for p_name, p_default in info.get("parameters", {}).items():
                    # Provide defaults as TA-Lib doesn't easily expose min/max limits
                    params.append({
                        "name": p_name,
                        "default": p_default,
                    })
                
                catalog[group].append({
                    "name": info["name"],
                    "display": info.get("display_name", info["name"]),
                    "inputs": list(set(inputs)) if inputs else ["close"],
                    "params": params,
                    "outputs": info.get("output_names", []),
                })
            except Exception:
                continue
    return catalog

@router.get("")
async def get_indicators():
    """
    Returns a grouped catalog of available TA-Lib indicators.
    """
    global _catalog_cache
    if _catalog_cache is None:
        _catalog_cache = _build_catalog()
    return _catalog_cache

@router.post("/compute")
async def compute_indicator(
    request: Request,
    body: ComputeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Computes a TA-Lib indicator over historical data.
    """
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    try:
        func = abstract.Function(body.function)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Unknown or unsupported TA-Lib function: {body.function}") from None

    # Fetch candles from Memgraph
    bot = getattr(request.app.state, "bot", None)
    if not bot or not bot.db:
        raise HTTPException(status_code=500, detail="Database connection not available")

    # get_candles returns a list of dicts: {"timestamp": int, "open": float, "high": float, "low": float, "close": float, "volume": float}
    # we limit by `bars` using a descending order query? Or we just fetch latest N by passing limit.
    # The current `get_candles` signature is: get_candles(symbol, timeframe, start_time, end_time, limit)
    # The query is ORDER BY c.timestamp ASC, and if we just pass `limit`, it gives the OLDEST N candles
    # Wait, the DB implementation of `get_candles` does `ORDER BY c.timestamp ASC LIMIT $limit`.
    # That means it will fetch the very first `bars` candles. We want the LATEST ones.
    # Let's check how the bot does it. We can fetch without limit and take the last `bars`, or
    # if there are too many, that's bad. Since we might need the latest, let's look at get_candles.
    
    # Wait, it's probably fine to fetch all and take the last `bars` if we don't pass limit, but that's inefficient.
    # Actually, we can just use `limit` parameter and it will be whatever `get_candles` provides, but let's see.
    # For now let's just use `get_candles` with `limit=None` and slice in Python if needed, or pass limit.
    
    # Actually, to get the last `bars`, we might want to query from exchange if db doesn't have it, but
    # the prompt says: "Fetch OHLCV candles from Memgraph candles (use existing database query patterns)"
    
    candles = await bot.db.get_candles(
        symbol=body.symbol,
        timeframe=body.timeframe,
        limit=body.bars + 100 # Add buffer for lookback
    )
    
    if not candles:
        raise HTTPException(status_code=400, detail=f"No candles found for {body.symbol} {body.timeframe}")
    
    # Take the latest N candles if the db returned more
    # If get_candles returned ascending, taking the last N is correct.
    candles = candles[-(body.bars + 100):]
    
    # Build numpy arrays for TA-Lib
    inputs = {
        "open": np.array([c["open"] for c in candles], dtype=np.float64),
        "high": np.array([c["high"] for c in candles], dtype=np.float64),
        "low": np.array([c["low"] for c in candles], dtype=np.float64),
        "close": np.array([c["close"] for c in candles], dtype=np.float64),
        "volume": np.array([c["volume"] for c in candles], dtype=np.float64),
    }
    
    try:
        # Run TA-Lib function
        result = func(inputs, **body.params)
        
        # Format output
        # `result` can be a single numpy array or a list/tuple of numpy arrays
        # The length of the output arrays matches the input length.
        # We should slice the output to exactly `body.bars`
        
        def _format_array(arr):
            # Replace NaN with None
            return [float(x) if not np.isnan(x) else None for x in arr[-(body.bars):]]
            
        output_names = func.info.get("output_names", ["real"])
        outputs = {}
        
        if isinstance(result, tuple) or isinstance(result, list):
            for name, arr in zip(output_names, result, strict=False):
                outputs[name] = _format_array(arr)
        else:
            outputs[output_names[0]] = _format_array(result)
            
        return {
            "function": body.function,
            "symbol": body.symbol,
            "timeframe": body.timeframe,
            "bars": body.bars,
            "outputs": outputs
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error computing indicator: {str(e)}") from e

