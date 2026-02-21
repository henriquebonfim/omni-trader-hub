# OmniTrader Roadmap

## Current: MVP (Phase 1)

**Status**: ✅ Implemented

A simple BTC/USDT Futures bot with:
- EMA(9/21) crossover strategy
- Volume confirmation
- Fixed position sizing (2%)
- Stop loss / Take profit
- Daily circuit breaker
- Discord alerts
- SQLite logging

---

## Phase 2: Strategy Enhancement (Weeks 5-8)

**Status**: 🔜 Planned

### Features
- [ ] **Regime Detection**: ADX indicator to filter trades (only trade in trends)
- [ ] **Multi-timeframe**: Confirm 15m signals with 1h trend direction
- [ ] **Trailing Stop**: Dynamic stop that follows price up
- [ ] **DCA Logic**: Add to position at better prices (max 2x)
- [ ] **Multiple Pairs**: Support ETH, SOL (one at a time)

### Success Criteria
- Sharpe ratio >1.0 on 3-month testnet data

---

## Phase 3: Production Pilot (Weeks 9-12)

**Status**: 🔜 Planned

### Milestones
- [ ] Switch to Binance mainnet
- [ ] Start with $100 real capital
- [ ] Never risk more than 5% of portfolio
- [ ] Daily manual review
- [ ] Emergency kill switch via Discord

### Success Criteria
- Profitable for 30 consecutive days

---

## Phase 4: Scale & Automate (Months 4-6)

**Status**: 🔮 Future

### Features
- [ ] Web dashboard (status page)
- [ ] Multiple pairs simultaneously
- [ ] Kelly Criterion position sizing
- [ ] vectorbt backtesting integration
- [ ] Cloud backup (GCP e2-micro failover)

### Success Criteria
- $1000+ capital, fully automated

---

## Phase 5: Intelligence Layer (Months 6-9)

**Status**: 🔮 Future

### Features
- [ ] Sentiment analysis (LunarCrush Fear/Greed)
- [ ] LLM daily reports (ministral-3b)
- [ ] News filter (pause on major events)
- [ ] Funding rate monitoring

### Success Criteria
- Sentiment improves Sharpe ratio by >0.2

---

## Phase 6: Full Architecture (Months 9-12+)

**Status**: 🔮 Future

The original vision from research:
- [ ] Microservices architecture (if needed)
- [ ] Streamer service (real-time WebSocket)
- [ ] Sentinel service (sentiment analysis)
- [ ] Quant service (backtesting, WFA)
- [ ] Strategist service (LLM reasoning)
- [ ] Guardian service (risk management)
- [ ] Full web dashboard with configuration

**Note**: May never need full architecture. Most profitable bots are simple.

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-20 | Start with single-service MVP | Prove concept before complexity |
| 2026-02-20 | EMA + Volume strategy | Simple, proven, debuggable |
| 2026-02-20 | Binance Futures testnet | Zero risk while learning |
| 2026-02-20 | No LLM in MVP | Not needed for technical strategy |
| 2026-02-20 | Discord for alerts | Already in use, simple setup |
