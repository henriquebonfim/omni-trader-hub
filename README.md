# OmniTrader MVP

A simple, working BTC/USDT Futures trading bot using EMA + Volume strategy.

## Features

- **Paper Trading Mode** - Test with $10k simulated balance using live market data
- **EMA(9/21) + Volume Strategy** - Trend-following with volume confirmation
- **Risk Management** - 2% position sizing, 2% SL, 4% TP, 5% daily circuit breaker
- **Discord Alerts** - Real-time notifications for all trading events
- **SQLite Logging** - Complete trade history with P&L tracking
- **Async Architecture** - Non-blocking, efficient market data handling

## Quick Start

### Option 1: Using Make (Recommended)

```bash
make install    # Create venv and install dependencies
make run        # Run in paper trading mode
make live       # Run with real money (requires API keys)
```

### Option 2: Manual Setup

```bash
# Install dependencies
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run the bot
python -m src.main
```

### 3. Configure (Optional)

Copy `.env.example` to `.env` for Discord alerts or live trading:

```bash
cp .env.example .env
```

Edit `.env`:
```
# For Discord alerts
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# For live trading (when paper_mode: false)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET=your_secret
```

### 4. Run the Bot

```bash
make run        # Paper trading (default)
make live       # Live trading
```

## Strategy

**EMA Crossover + Volume Confirmation**

| Signal | Condition |
|--------|-----------|
| LONG | EMA(9) crosses above EMA(21) + Volume > 1.5x average |
| SHORT | EMA(9) crosses below EMA(21) + Volume > 1.5x average |
| EXIT | Opposite EMA cross or SL/TP hit |

## Risk Management

| Parameter | Value |
|-----------|-------|
| Position Size | 2% of wallet |
| Stop Loss | 2% |
| Take Profit | 4% (2:1 R:R) |
| Daily Loss Limit | 5% (circuit breaker) |
| Leverage | 3x isolated |

## Project Structure

```
OmniTrader/
├── src/
│   ├── main.py       # Entry point, main loop
│   ├── config.py     # Configuration management
│   ├── exchange.py   # Binance Futures wrapper
│   ├── strategy.py   # EMA + Volume strategy
│   ├── risk.py       # Risk management
│   ├── notifier.py   # Discord alerts
│   └── database.py   # SQLite logging
├── config/
│   └── config.yaml   # Configuration
├── data/
│   └── trades.db     # Trade history (auto-created)
└── .env              # API keys (create from .env.example)
```

## Discord Alerts

The bot sends alerts for:
- 🟢 Long positions opened
- 🔴 Short positions opened
- ✅ Profitable trades closed
- ❌ Losing trades closed
- ⚠️ Circuit breaker triggered
- 🚨 Errors

## Configuration

Edit `config/config.yaml` to customize:

```yaml
trading:
  symbol: BTC/USDT:USDT     # Trading pair
  timeframe: 15m            # Candle timeframe
  position_size_pct: 2.0    # Risk per trade

strategy:
  ema_fast: 9               # Fast EMA period
  ema_slow: 21              # Slow EMA period
  volume_threshold: 1.5     # Volume multiplier

risk:
  stop_loss_pct: 2.0        # Stop loss %
  take_profit_pct: 4.0      # Take profit %
  max_daily_loss_pct: 5.0   # Circuit breaker
```

## Future Roadmap

This MVP is the foundation for a larger system. See [docs/ROADMAP.md](docs/ROADMAP.md) for:
- Phase 2: Regime detection, trailing stops, DCA
- Phase 3: Production pilot with real money
- Phase 4: Web dashboard, multiple pairs
- Phase 5: Sentiment analysis, LLM integration
- Phase 6: Full microservices architecture

## License

Personal project - not for commercial use.
