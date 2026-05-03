from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(prefix="/candles", tags=["candles"])


@router.get("/")
async def get_candles(
    request: Request,
    symbol: str | None = Query(None, description="Trading pair like BTC/USDT"),
    timeframe: str = Query(..., description="Timeframe like 1m, 5m, 1h, 1d"),
    limit: int = Query(200, ge=10, le=1000, description="Max number of candles"),
):
    bot = request.app.state.bot
    symbol = symbol or bot.config.trading.symbol

    # Only allow exchange-supported timeframes. Aliases are exact conversions,
    # not approximations/fallbacks.
    tf_aliases = {
        "1 sec": "1s",
        "1 min": "1m",
        "3 min": "3m",
        "5 min": "5m",
        "15 min": "15m",
        "30 min": "30m",
        "1 hour": "1h",
        "2 hours": "2h",
        "4 hours": "4h",
        "6 hours": "6h",
        "8 hours": "8h",
        "12 hours": "12h",
        "1D": "1d",
        "3D": "3d",
        "1W": "1w",
        "1M": "1M",
    }

    normalized_tf = tf_aliases.get(timeframe, timeframe)

    # Prefer exchange-advertised supported values; fallback to known Binance set.
    supported = set((getattr(bot.exchange.client, "timeframes", None) or {}).keys())
    if not supported:
        supported = {
            "1s",
            "1m",
            "3m",
            "5m",
            "15m",
            "30m",
            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",
            "1d",
            "3d",
            "1w",
            "1M",
        }

    if normalized_tf not in supported:
        supported_list = ", ".join(sorted(supported))
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported timeframe '{timeframe}'. Supported values: {supported_list}",
        )

    try:
        ohlcv = await bot.exchange.client.fetch_ohlcv(
            symbol, normalized_tf, limit=limit
        )

        # Format for lightweight-charts
        # [timestamp, open, high, low, close, volume]
        formatted = [
            {
                "time": candle[0] / 1000,  # seconds
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "value": candle[5],  # volume
            }
            for candle in ohlcv
        ]

        return {"ok": True, "data": formatted}
    except Exception as e:
        return {"ok": False, "message": str(e)}
