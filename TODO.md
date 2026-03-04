# TODO

Confirmed work for the current sprint. All items validated, scoped, and ready to implement.
Promoted from TASKS.md after institutional audit (2026-03-03).

> Last updated: 2026-03-03 by Institutional Audit

---

> **⚠️ GEOPOLITICAL CONTEXT (2026-03-03):** Day 3 of US-Israeli war with Iran. Strait of Hormuz closed. Extreme macro volatility expected — oil spike, risk-off cascade, BTC correlation shift. **DO NOT deploy live capital until these items are resolved AND the crisis stabilizes.**

## Sprint: Post-Audit Critical Fixes

### 1. Fix SL/TP Failure → Retry or Flatten (T6) ✅
- [x] In `_open_position()`: after SL placement fails, retry 3× with 1s backoff
- [x] If all retries fail, immediately call `_close_position()` to flatten
- [x] Same pattern for TP placement failure
- [x] Add test: mock SL failure → verify position is flattened
- **Ref**: TASKS.md T6
- **Completed**: 2026-03-03 | Commit 59a9dce

### 2. Fix Paper Mode PnL Formula (T7) ✅
- [x] Change formula to `(exit_price - entry_price) * contracts` (long) / negate for short
- [x] Match the live-mode formula already used in `main.py _close_position()`
- [x] Add test: verify paper PnL matches manual calculation for long and short
- **Ref**: TASKS.md T7
- **Completed**: 2026-03-04 | PR #51

### 3. Add Paper SL/TP Simulation (T8) ✅
- [x] Add `_check_paper_orders()` method that checks paper orders vs current price each cycle
- [x] Trigger SL/TP fills when price crosses levels
- [x] Add test: verify paper SL triggers on adverse price move
- **Ref**: TASKS.md T8
- **Completed**: 2026-03-04 | PR #52

### 4. Wire ATR Stops to Exchange Orders (T9)
- [ ] Pass `ohlcv` DataFrame to `validate_trade()` in `_open_position()`
- [ ] When `use_atr_stops` is enabled, use ATR-derived prices for `set_stop_loss()` / `set_take_profit()`
- [ ] Fallback to fixed % if OHLCV data insufficient for ATR calculation
- [ ] Add test: verify ATR stop prices are used when config enabled
- **Ref**: TASKS.md T9

### 5. Fix `current_positions` Hardcoded to 0 (T10)
- [ ] Query actual open position count from exchange state
- [ ] Change `max_positions` config from 50 to 1 (single-asset)
- [ ] Add test: verify second position blocked when max_positions=1
- **Ref**: TASKS.md T10

### 6. Add Auth to All Mutation Endpoints (T11)
- [ ] Add `verify_api_key` dependency to: `/api/bot/*`, `PUT /api/config`, `PUT /api/notifications/*`
- [ ] Verify all GET endpoints remain readable (status, health)
- [ ] Add tests: verify 401 on unauthenticated mutation
- **Ref**: TASKS.md T11

### 7. Add Regime Hysteresis (T13)
- [ ] Implement Schmitt-trigger: enter TRENDING at ADX > 28, exit at ADX < 22
- [ ] Same for VOLATILE: enter at ATR > 1.7× baseline, exit at ATR < 1.3× baseline
- [ ] Persist `current_regime` between cycles (already in memory, just add hysteresis)
- [ ] Add test: verify regime doesn't flip when ADX oscillates between 23-27
- **Ref**: TASKS.md T13

### 8. Add Entry Cooldown for Level-Based Strategies (T15)
- [ ] Add `_last_entry_bar` tracking in `BaseStrategy`
- [ ] Add `min_bars_between_entries` config param (default: 10)
- [ ] Block new entries for N bars after any entry on same side
- [ ] Add test: verify re-entry blocked within cooldown window
- **Ref**: TASKS.md T15
