"""
Verify SMC Analysis on Live Data.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.exchange import Exchange
from src.strategies.smc.analysis import SMCAnalyzer
from src.config import get_config

async def main():
    print("Initializing Exchange...")
    exchange = Exchange()
    await exchange.connect()

    symbol = exchange.config.trading.symbol
    print(f"Analyzing {symbol}...")

    # Fetch data
    timeframes = ["4h", "1h", "15m"]
    market_data = {}

    for tf in timeframes:
        print(f"Fetching {tf}...")
        try:
            df = await exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
            market_data[tf] = df
            print(f"  Fetched {len(df)} candles. Last close: {df['close'].iloc[-1]}")
        except Exception as e:
            print(f"  Failed to fetch {tf}: {e}")
            print("  Generating synthetic data instead...")

            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta

            # Generate synthetic uptrend
            dates = [datetime.now() - timedelta(hours=i) for i in range(200)]
            dates.reverse()

            # Simple sine wave + trend
            x = np.linspace(0, 4*np.pi, 200)
            trend = np.linspace(100, 110, 200)
            price = trend + np.sin(x) * 2

            df = pd.DataFrame({
                "open": price, "high": price + 0.5, "low": price - 0.5, "close": price, "volume": 1000
            }, index=dates)
            market_data[tf] = df

    # Analyze
    print("\nRunning SMC Analysis...")
    analyzer = SMCAnalyzer(swing_window=5)
    results = analyzer.analyze(market_data)

    for tf, res in results.items():
        print(f"\nTimeframe: {tf}")
        print(f"  Trend: {res.trend.name}")

        last_high = res.last_swing_high
        last_low = res.last_swing_low

        if last_high:
            print(f"  Last High: {last_high.price} (Index: {last_high.index})")
        if last_low:
            print(f"  Last Low:  {last_low.price} (Index: {last_low.index})")

        if res.last_bos:
            print(f"  Last BOS:  {res.last_bos.type} {res.last_bos.trend.name} @ {res.last_bos.price} (Time: {res.last_bos.time})")

        if res.last_choch:
            print(f"  Last CHoCH:{res.last_choch.type} {res.last_choch.trend.name} @ {res.last_choch.price} (Time: {res.last_choch.time})")

    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
