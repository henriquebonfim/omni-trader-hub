from fastapi import APIRouter, Request, Query

router = APIRouter(prefix="/candles", tags=["candles"])

@router.get("/")
async def get_candles(
    request: Request,
    timeframe: str = Query(..., description="Timeframe like 1m, 5m, 1h, 1d")
):
    bot = request.app.state.bot
    symbol = bot.config.trading.symbol
    
    # Map requested timeframe to CCXT supported timeframe
    # CCXT/Binance doesn't support "sec", "years" natively in fetch_ohlcv.
    # We will map user requests to closest supported, or just pass it to CCXT.
    
    # Binance supports: 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    tf_map = {
        "1 sec": "1s",
        "10 sec": "1s", # no 10s, fallback
        "30 sec": "1s",
        "1 min": "1m",
        "5 min": "5m",
        "15 min": "15m",
        "30 min": "30m",
        "1 hour": "1h",
        "3 hours": "1h", # no 3h, fallback to 1h and we'd have to aggregate, but let's try 1h
        "12 hours": "12h",
        "1D": "1d",
        "3D": "3d",
        "5D": "3d",
        "7D": "1w",
        "15D": "1w",
        "1Y": "1M",
        "3Y": "1M",
        "5Y": "1M",
        "7Y": "1M",
        "9Y": "1M"
    }
    
    mapped_tf = tf_map.get(timeframe, timeframe)
    
    try:
        limit = 1000
        ohlcv = await bot.exchange.client.fetch_ohlcv(symbol, mapped_tf, limit=limit)
        
        # Format for lightweight-charts
        # [timestamp, open, high, low, close, volume]
        formatted = [
            {
                "time": candle[0] / 1000, # seconds
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "value": candle[5] # volume
            }
            for candle in ohlcv
        ]
        
        return {"ok": True, "data": formatted}
    except Exception as e:
        return {"ok": False, "message": str(e)}
