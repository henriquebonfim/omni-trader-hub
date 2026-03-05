# TODO

Confirmed work for the current sprint. All items validated, scoped, and ready to implement.
Promoted from TASKS.md after institutional audit and v1.0.0 release.

> Last updated: 2026-03-05 | Sprint: Post-v1.0.0 Validation & Safety

---

> **⚠️ GEOPOLITICAL CONTEXT (2026-03-05):** Day 5 of US-Israeli war with Iran. Strait of Hormuz closed. Extreme macro volatility continues — oil spike, risk-off cascade, BTC correlation shift. **T30 (Geopolitical Risk Module) is HIGH PRIORITY for this sprint.**

## Sprint: Post-v1.0.0 — Validation & Safety Phase

**Status**: v1.0.0 shipped with all critical audit findings resolved. This sprint focuses on statistical validation (backtesting) and live trading safety mechanisms before deploying capital.

### 1. Build Backtesting Engine (T29)
- [ ] **Phase 1**: Historical data ingestion (Binance `/api/v3/klines`)
    - Create `src/backtest/data.py` with OHLCV download & caching
    - Support date range queries, multiple timeframes
    - Cache to local SQLite or CSV for reproducibility
- [ ] **Phase 2**: Event-driven simulation engine
    - Implement `src/backtest/engine.py` with proper lookahead bias prevention
    - Process bars chronologically, only use data available at each timestamp
    - Support multiple strategies running in parallel
- [ ] **Phase 3**: Cost model integration
    - Model spread (bid-ask), commission (0.04% maker/taker), slippage (configurable)
    - Add funding rate costs for positions held overnight
    - Document assumptions in backtest results
- [ ] **Phase 4**: Walk-forward validation
    - Implement rolling or expanding window framework
    - Minimum 6-month out-of-sample holdout for final validation
    - Generate train/test split reports
- [ ] **Phase 5**: Performance metrics & reporting
    - Calculate: Sharpe, Sortino, max drawdown, profit factor, win rate, avg win/loss
    - Bootstrap validation (1000+ runs) for confidence intervals
    - Export results to JSON + visual equity curve
- **Ref**: TASKS.md T29 | **Priority**: 🔴 CRITICAL

### 2. Geopolitical & Macro Risk Module (T30)
- [ ] **Phase 1**: Data source integration
    - Integrate Fear & Greed Index API (Alternative.me)
    - Add DXY (dollar index) via FRED or Yahoo Finance
    - Add oil futures price tracking (Hormuz proxy)
    - Add crypto VIX equivalent (e.g., Deribit DVOL)
- [ ] **Phase 2**: Crisis-mode protocol
    - Add `crisis_mode: bool` field to `config.yaml`
    - When enabled: leverage → 1×, position_size_pct → 0.5%, only ADX strategy, daily_loss_pct → 2%
    - Persist crisis mode state in Redis (survives restarts)
- [ ] **Phase 3**: Sentiment-reality divergence detector
    - Flag when Fear & Greed > 75 (Extreme Greed) + elevated geopolitical risk
    - Reduce signal confidence scores by 50% during divergence
    - Log warnings to notify system
- [ ] **Phase 4**: Dashboard integration
    - Add `/api/macro/status` endpoint returning current macro state
    - Add crisis mode toggle in frontend `ConfigEditor.tsx`
    - Display macro indicators in dashboard (DXY, oil, VIX, Fear & Greed)
- **Ref**: TASKS.md T30 | **Priority**: 🟠 HIGH

### 3. Semi-Automatic Mode (T31)
- [ ] **Phase 1**: Backend approval queue
    - Add `semi_automatic_mode: bool` to config
    - When enabled, save signals to `pending_signals` table instead of executing
    - Include: symbol, side, entry_price, sl, tp, reasoning, timestamp
    - Auto-reject signals older than 60s (stale)
- [ ] **Phase 2**: Frontend approval UI
    - Create `SignalApproval.tsx` component
    - Show pending signal details + risk metrics
    - Buttons: Approve (execute), Reject (skip), Modify (adjust size/stops)
    - WebSocket push notification on new signal
- [ ] **Phase 3**: Approval logging & analytics
    - Log all approval/reject decisions with timestamp and reason
    - Track approval rate, avg decision time
    - After 20 approved trades or 2 weeks, suggest auto mode
- **Ref**: TASKS.md T31 | **Priority**: 🟠 HIGH

---

## Completed Sprints

<details>
<summary>Sprint: Post-Audit Critical Fixes (2026-03-03 to 2026-03-04) — ✅ COMPLETE</summary>

### 1. Fix SL/TP Failure → Retry or Flatten (T6) ✅
- [x] In `_open_position()`: after SL placement fails, retry 3× with 1s backoff
- [x] If all retries fail, immediately call `_close_position()` to flatten
- [x] Same pattern for TP placement failure
- [x] Add test: mock SL failure → verify position is flattened
- **Ref**: TASKS.md T6
- **Completed**: 2026-03-03 | Commit 59a9dce | **Status**: ✅ COMPLETE

### 2. Fix Paper Mode PnL Formula (T7) ✅
- [x] Change formula to `(exit_price - entry_price) * contracts` (long) / negate for short
- [x] Match the live-mode formula already used in `main.py _close_position()`
- [x] Add test: verify paper PnL matches manual calculation for long and short
- **Ref**: TASKS.md T7
- **Completed**: 2026-03-04 | PR #51 | **Status**: ✅ COMPLETE

### 3. Add Paper SL/TP Simulation (T8) ✅
- [x] Add `_check_paper_orders()` method that checks paper orders vs current price each cycle
- [x] Trigger SL/TP fills when price crosses levels
- [x] Add test: verify paper SL triggers on adverse price move
- **Ref**: TASKS.md T8
- **Completed**: 2026-03-04 | PR #52 | **Status**: ✅ COMPLETE

### 4. Wire ATR Stops to Exchange Orders (T9) ✅
- [x] Pass `ohlcv` DataFrame to `validate_trade()` in `_open_position()`
- [x] When `use_atr_stops` is enabled, use ATR-derived prices for `set_stop_loss()` / `set_take_profit()`
- [x] Fallback to fixed % if OHLCV data insufficient for ATR calculation
- [x] Add test: verify ATR stop prices are used when config enabled
- **Ref**: TASKS.md T9
- **Completed**: 2026-03-04 | PR #53 | **Status**: ✅ COMPLETE

### 5. Fix `current_positions` Hardcoded to 0 (T10) ✅
- [x] Query actual open position count from exchange state
- [x] Change `max_positions` config from 50 to 1 (single-asset)
- [x] Add test: verify second position blocked when max_positions=1
- **Ref**: TASKS.md T10
- **Completed**: 2026-03-04 | PR #54 | **Status**: ✅ COMPLETE

### 6. Add Auth to All Mutation Endpoints (T11) ✅
- [x] Add `verify_api_key` dependency to: `/api/bot/*`, `PUT /api/config`, `PUT /api/notifications/*`
- [x] Verify all GET endpoints remain readable (status, health)
- [x] Add tests: verify 401 on unauthenticated mutation
- **Ref**: TASKS.md T11
- **Completed**: 2026-03-04 | PR #55 | **Status**: ✅ COMPLETE

### 7. Add Regime Hysteresis (T13) ✅
- [x] Implement Schmitt-trigger: enter TRENDING at ADX > 28, exit at ADX < 22
- [x] Same for VOLATILE: enter at ATR > 1.7× baseline, exit at ATR < 1.3× baseline
- [x] Persist `current_regime` between cycles (already in memory, just add hysteresis)
- [x] Add test: verify regime doesn't flip when ADX oscillates between 23-27
- **Ref**: TASKS.md T13
- **Completed**: 2026-03-04 | PR #56 | **Status**: ✅ COMPLETE

### 8. Add Entry Cooldown for Level-Based Strategies (T15) ✅
- [x] Add `_last_entry_bar` tracking in `BaseStrategy`
- [x] Add `min_bars_between_entries` config param (default: 10)
- [x] Block new entries for N bars after any entry on same side
- [x] Add test: verify re-entry blocked within cooldown window
- **Ref**: TASKS.md T15
- **Completed**: 2026-03-04 | PR #57 | **Status**: ✅ COMPLETE

</details>
