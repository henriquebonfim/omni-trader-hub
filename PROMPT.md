# OmniTrader — Full-Stack Dashboard Specification

> **Purpose**: Complete frontend for a multi-asset autonomous crypto trading bot.
> The bot trades **any cryptocurrency pair** on Binance Futures, automatically selects
> and rotates strategies per-asset based on regime + backtesting performance, and
> exposes full control through this dashboard.

---

## Tech Stack

- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 (dark theme)
- **Charts**: Lightweight Charts (TradingView) + Recharts for analytics
- **State**: TanStack Query v5 for API, Zustand for local state
- **WebSocket**: Native WebSocket with exponential-backoff reconnection
- **HTTP**: Fetch with typed wrappers
- **Icons**: Lucide React
- **Tables**: TanStack Table v8 (sorting, filtering, pagination)

---

## Design System

### Colors (CSS Variables)
```css
:root {
  --bg-base: #0d0f14;
  --bg-panel: #161b22;
  --bg-hover: #21262d;
  --bg-input: #0d1117;
  --border: #30363d;
  --text-primary: #e6edf3;
  --text-secondary: #8b949e;
  --text-muted: #484f58;
  --accent: #58a6ff;
  --accent-dim: #1f3a5f;
  --green: #3fb950;
  --red: #f85149;
  --yellow: #d29922;
  --orange: #f0883e;
  --purple: #bc8cff;
  --cyan: #39d2c0;

  --sentiment-pos: #3fb950;
  --sentiment-neu: #8b949e;
  --sentiment-neg: #f85149;
  --impact-high: #f85149;
  --impact-med: #d29922;
  --impact-low: #58a6ff;
  --crisis-bg: rgba(248, 81, 73, 0.1);
  --radius: 8px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}
```

### Typography
- Font: Inter (import from Google Fonts), fallback system stack
- Base: 14px, Line height: 1.5
- Headings: 20px (h1), 18px (h2), 16px (h3), 14px (h4)
- Monospace (numbers / code): JetBrains Mono or font-mono

### Spacing & Sizing
- Panel padding: 16px
- Grid gap: 16px
- Border radius: 8px (panels), 6px (buttons/inputs), 4px (badges)

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│ TOPBAR (48px)                                        │
│ [●] OmniTrader   [Asset Picker ▼]  Paper │ WS ● │ 🔔│
├────────────┬─────────────────────────────────────────┤
│ SIDEBAR    │ MAIN CONTENT                            │
│ (220px)    │ (scrollable, p-24)                      │
│            │                                         │
│ Navigation │                                         │
│ items      │                                         │
│            │                                         │
│ ─────────  │                                         │
│ Active     │                                         │
│ Bots       │                                         │
│ Summary    │                                         │
└────────────┴─────────────────────────────────────────┘
```

### Topbar
- Left: Status dot (green running / red stopped) + "OmniTrader" logo text
- Center: **Asset Picker** dropdown — shows currently active pairs (e.g. "BTC/USDT, ETH/USDT, SOL/USDT") with a count badge. Click opens multi-select.
- Right group: Paper/Live mode badge, WS connection dot, Notification bell (unread count), Settings gear icon

### Sidebar Navigation (9 pages)
```
📊  Dashboard
🤖  Bots & Assets
🧠  Intelligence
📈  Charts
🎯  Backtesting
🛡️  Risk Monitor
📋  Trade History
🧪  Strategy Lab
⚙️  Settings
```

### Sidebar Bottom Section — Active Bots Summary
Below the navigation, show a mini summary:
- Total active bots count
- Combined PnL today
- Combined balance
- Collapsed by default on mobile

---

## Core Concept: Multi-Asset Autonomous Bots

The system runs **one bot per asset pair**. Each bot:
1. Scans current market regime (TRENDING / RANGING / VOLATILE)
2. **Auto-selects the best strategy** based on regime + historical backtest performance
3. Manages its own position, SL/TP, and risk independently
4. The user can override strategy selection per-bot or lock a specific strategy

```typescript
interface Bot {
  id: string
  symbol: string                    // "BTC/USDT", "ETH/USDT", etc.
  status: 'running' | 'stopped' | 'paused' | 'error'
  mode: 'auto' | 'manual'          // auto = bot picks strategy, manual = user locks one
  active_strategy: string           // current strategy name
  regime: 'trending' | 'ranging' | 'volatile'
  position: Position | null
  daily_pnl: number
  daily_pnl_pct: number
  balance_allocated: number
  leverage: number
  created_at: number
}

interface Position {
  side: 'long' | 'short'
  entry_price: number
  size: number
  unrealized_pnl: number
  stop_loss: number
  take_profit: number
  opened_at: number
}
```

---

## API Structure

### REST Endpoints
```typescript
// Health & Status
GET  /api/health
GET  /api/status                              // global status + list of active bots

// Bot Management (multi-asset)
GET  /api/bots                                // list all bots
POST /api/bots                                // create new bot { symbol, mode, strategy?, leverage, allocation }
GET  /api/bots/{id}                           // single bot detail
PUT  /api/bots/{id}                           // update bot config
DELETE /api/bots/{id}                         // remove bot
POST /api/bots/{id}/start
POST /api/bots/{id}/stop
POST /api/bots/{id}/trade/open               // manual trade on specific bot
POST /api/bots/{id}/trade/close

// Strategies
GET  /api/strategies                          // list all available strategies (built-in + custom)
GET  /api/strategies/{name}                   // strategy detail + parameters
POST /api/strategies                          // save custom strategy
PUT  /api/strategies/{name}                   // update custom strategy
DELETE /api/strategies/{name}                 // delete custom strategy (only user-created)

// Analytics & History
GET  /api/trades/history?symbol=&limit=&offset=
GET  /api/equity/snapshots?symbol=&days=
GET  /api/slippage/analysis?symbol=

// Intelligence / Graph
GET  /api/graph/sentiment/{symbol}
GET  /api/graph/crisis
PUT  /api/graph/crisis
GET  /api/graph/news

// Backtesting
POST /api/backtest/run
GET  /api/backtest/results/{id}
GET  /api/backtest/history

// Configuration
GET  /api/config
PUT  /api/config

// Environment Variables
GET  /api/env                                 // list all env vars (values masked for secrets)
PUT  /api/env                                 // update env vars (requires auth, restarts services)

// Available Markets
GET  /api/markets                             // fetch tradeable pairs from exchange
```

### WebSocket Messages (ws://localhost:8000/ws)
```typescript
// Server sends one message per bot per cycle
interface CycleMessage {
  type: 'cycle_update'
  bot_id: string
  symbol: string
  timestamp: number
  price: number
  signal: 'LONG' | 'SHORT' | 'HOLD' | 'EXIT_LONG' | 'EXIT_SHORT'
  active_strategy: string
  regime: 'trending' | 'ranging' | 'volatile'
  position: 'long' | 'short' | null
  balance: number
  daily_pnl: number
  daily_pnl_pct: number
  circuit_breaker: boolean
  reason?: string

  // Intelligence overlay
  sentiment?: number
  crisis_mode?: boolean
  macro_indicators?: {
    fear_greed: number
    dxy: number
    oil: number
    btc_dominance: number
  }
  divergence_flag?: boolean
}

// Global alerts
interface AlertMessage {
  type: 'alert'
  level: 'info' | 'warning' | 'critical'
  title: string
  body: string
  timestamp: number
}

// Trade execution events
interface TradeMessage {
  type: 'trade'
  bot_id: string
  symbol: string
  action: 'OPEN' | 'CLOSE'
  side: 'long' | 'short'
  price: number
  size: number
  pnl?: number
  strategy: string
  timestamp: number
}
```

---

## Page 1: 📊 Dashboard

### 1.1 GlobalStatsBar (top row, full width)
- Total portfolio value (sum of all bots)
- Today's combined PnL ($ and %)
- Active bots count / total bots
- Open positions count
- Global circuit breaker status
- Sentiment gauge (mini, from intelligence)

### 1.2 BotGridCards
Grid of cards, one per active bot. Each card shows:
- Symbol name + icon (e.g. BTC logo)
- Status badge (Running/Stopped/Error)
- Current price (live from WS)
- Active strategy name + mode badge (Auto/Manual)
- Regime badge (TRENDING ▲ / RANGING ↔ / VOLATILE ⚡)
- Position status (LONG/SHORT/FLAT with color)
- Unrealized PnL (if position open)
- Daily PnL with sparkline
- Quick actions: [Pause] [Stop] [Details →]

### 1.3 EquityCurveChart
- Combined equity curve for all bots or select single bot
- Toggle: [Combined] [Per Bot]
- Timeframe tabs: 1D, 7D, 30D, ALL
- Y-axis: dollar amount, X-axis: time
- Hover tooltip with exact values

### 1.4 RecentTradesTable (compact, last 10)
- Columns: Time, Symbol, Side, Strategy, PnL
- Click row → goes to Trade History with filters applied
- Color coding (green/red)

### 1.5 AlertsFeed (right sidebar or bottom panel)
- Live streaming alerts from WS
- Types: trade executions, circuit breaker triggers, regime changes, strategy rotations
- Filterable by severity
- Bell icon in topbar shows unread count

---

## Page 2: 🤖 Bots & Assets

### 2.1 BotManagementTable
Full CRUD table for all bots (active + stopped):

| Symbol | Status | Mode | Strategy | Regime | Position | Daily PnL | Balance | Actions |
|--------|--------|------|----------|--------|----------|-----------|---------|---------|
| BTC/USDT | ● Running | Auto | ADX Trend | TRENDING | LONG +1.2% | +$45 | $5,000 | [⏸ ■ ⚙] |
| ETH/USDT | ● Running | Manual | Bollinger | RANGING | FLAT | +$12 | $3,000 | [⏸ ■ ⚙] |
| SOL/USDT | ○ Stopped | Auto | — | — | — | $0 | $2,000 | [▶ ✕ ⚙] |

Actions per row: Start/Pause/Stop, Delete (with confirmation), Configure (opens drawer)

### 2.2 AddBotDrawer (slide-in from right)
Form to create a new bot:
- **Symbol Picker**: Searchable dropdown. Fetch tradeable pairs from `GET /api/markets`. Show symbol + 24h volume + last price. Filter by quote currency (USDT, BUSD).
- **Mode**: Radio — "Auto (bot selects strategy)" or "Manual (lock strategy)"
- **Strategy Selector**: Only visible in Manual mode. Dropdown of all strategies from `GET /api/strategies`.
- **Allocation**: Slider or number input — % of total capital to allocate to this bot
- **Leverage**: Slider 1x–10x (default 3x)
- **Timeframe**: Radio buttons — 5m, 15m, 1h, 4h
- **Risk Overrides** (collapsible):
  - Max daily loss %
  - Stop loss mode (Fixed % / ATR-based)
  - Position size %
- [Create Bot] button

### 2.3 BotDetailDrawer (when clicking a bot row)
- Full detail view of single bot
- Tabs: Overview | Position | Trades | Strategy | Risk
- **Overview**: all stats, current state, last 5 signals
- **Position**: current or last position details, SL/TP levels, trailing stop
- **Trades**: filtered trade history for this bot
- **Strategy**: which strategy is active, why it was selected (regime match), performance of strategy on this asset
- **Risk**: bot-specific risk metrics, circuit breaker states

---

## Page 3: 🧠 Intelligence

### 3.1 SentimentOverviewCard
- Large emoji face scaled by sentiment (-1 to +1)
- Label: "Very Bearish" → "Bearish" → "Neutral" → "Bullish" → "Very Bullish"
- Volume badge: "42 articles in last 24h"
- Max impact indicator

### 3.2 CrisisModePanel
- Status: Large "NORMAL TRADING" (green) or "CRISIS MODE ACTIVE" (red, pulsing border)
- Override display when active: Leverage 1x, Position 0.5%, ADX Trend only
- [Toggle Crisis Mode] button (auth required)
- Trigger source: "Auto-detected" or "Manual"

### 3.3 MacroIndicatorsGrid (2×2)
Four cards:
- **Fear & Greed Index**: 0–100 gauge, color (Extreme Fear → Extreme Greed), change arrow
- **DXY (Dollar Index)**: Value, %, trend arrow
- **Oil (WTI)**: Value, %, trend arrow
- **BTC Dominance**: Value, %, trend arrow

### 3.4 AlertsBanner
- Dismissible warnings for divergence detection
- Priority colors: info (blue), warning (yellow), critical (red)

### 3.5 NewsFeedList (scrollable)
```typescript
interface NewsItem {
  id: string
  title: string
  source: string
  published_at: number
  sentiment_score: number
  impact_level: number       // 0–1
  assets: string[]
  sectors: string[]
}
```
- Impact badge (🔴 HIGH / 🟡 MED / 🟢 LOW)
- Source, sentiment emoji + score, relative timestamp
- Asset + Sector pill tags
- Filter tabs: [All] [High Impact] [By Asset]

### 3.6 CorrelationMatrix
- Heatmap of all active bot pairs
- Color scale: red (high) → blue (low)
- Hover shows exact coefficient

---

## Page 4: 📈 Charts

### 4.1 AssetSelector (top)
- Dropdown: pick any active bot's symbol
- Or type to search any pair

### 4.2 CandlestickChart (main, takes ~70% height)
- Lightweight Charts library
- Timeframe tabs: 5m, 15m, 1h, 4h, 1d
- Volume bars below candles
- Overlay markers:
  - BUY/SELL arrows at trade execution points
  - SL/TP horizontal lines for open positions
  - Regime shaded zones (green=trending, blue=ranging, orange=volatile)
- Fullscreen toggle

### 4.3 IndicatorsPanel (below chart or sidebar)
Current indicator values for the selected asset:
- EMA(9), EMA(21), SMA(50)
- RSI(14), MACD, Stochastic
- Bollinger Bands (upper/mid/lower)
- ATR(14), ADX
- Any custom indicator values from active strategy

### 4.4 RegimeCard
- Current regime badge + confidence score
- ADX value, ATR value
- Bias: BULLISH ↑ / BEARISH ↓ / NEUTRAL

---

## Page 5: 🎯 Backtesting

### 5.1 BacktestConfigForm
```typescript
interface BacktestConfig {
  symbol: string             // any pair, searchable dropdown
  start_date: string
  end_date: string
  strategy: string           // dropdown from GET /api/strategies (built-in + custom)
  timeframe: string          // 5m, 15m, 1h, 4h, 1d
  initial_capital: number
  position_size_pct: number
  leverage: number
}
```
- [▶ Run Backtest] button with progress bar
- Preset buttons: "Bear Market 2022", "Bull Run 2024", "Last 6 Months"

### 5.2 BacktestMetricsGrid (4×3)
```typescript
interface BacktestResults {
  total_pnl: number
  total_return_pct: number
  sharpe_ratio: number          // target >1.0
  sortino_ratio: number         // target >1.5
  max_drawdown_pct: number      // target <15%
  profit_factor: number         // target >1.5
  win_rate_pct: number          // target >45%
  avg_win_loss_ratio: number
  total_trades: number
  wins: number
  losses: number
  avg_trade_duration_hours: number
  best_trade_pnl: number
  worst_trade_pnl: number
}
```
Each metric shows value + target pass/fail badge (✅/❌)

### 5.3 BacktestEquityChart
- Line chart with drawdown overlay (shaded red area)
- Trade markers (green/red dots)
- Toggle: linear / log scale
- [Export PNG] [Export CSV]

### 5.4 MonthlyReturnsHeatmap
- Grid: rows = years, columns = months
- Color: green (positive) → red (negative)
- Hover shows exact %

### 5.5 WalkForwardTable
- Window dates, in-sample Sharpe, out-of-sample Sharpe, degradation %
- Row status: ✅ if degradation <15%

### 5.6 BootstrapCI
- Confidence intervals for Sharpe, max DD, profit factor
- Display: "1.42 [95% CI: 1.18 – 1.65]"

### 5.7 BacktestTradeLog
- Paginated table (50 per page)
- Columns: Date, Symbol, Side, Entry, Exit, PnL, Reason
- Sortable, filterable, export to CSV

---

## Page 6: 🛡️ Risk Monitor

### 6.1 GlobalRiskOverview
- Total portfolio exposure ($ and %)
- Total allocated capital
- Combined drawdown from HWM
- Number of open positions across all bots

### 6.2 CircuitBreakersPanel
Five rows, each with: Name, limit, current value, progress bar (green→yellow→red), status badge

| Circuit Breaker | Limit | Current | Status |
|----------------|-------|---------|--------|
| Daily Loss | -5% | -1.2% | ✅ OK |
| Consecutive Losses | 3 max | 1 | ✅ OK |
| Weekly Loss | -10% | -3.5% | ✅ OK |
| Black Swan | >10% move | 2.1% | ✅ OK |
| Volatility Spike | >3× ATR | 1.8× | ✅ OK |

### 6.3 PerBotRiskGrid
Table showing risk metrics per active bot:

| Bot | Exposure | Leverage | Liq. Distance | DD from HWM | CB Status |
|-----|----------|----------|---------------|-------------|-----------|
| BTC | $612 (6%) | 3× | 33% ✅ | -1.9% | OK |
| ETH | $420 (4%) | 3× | 28% ⚠️ | -3.2% | OK |

### 6.4 DrawdownTracker
- Peak equity ($ + date)
- Current equity
- Drawdown bar: value / trigger threshold
- Auto-deleverage status

### 6.5 StreakTracking
- Current streak, longest win/loss, size multiplier

---

## Page 7: 📋 Trade History

### 7.1 PnLSummaryBar (top)
- Total trades, total PnL, win rate, avg win/loss, largest win/loss
- Period selector: Today, Week, Month, All

### 7.2 TradeHistoryTable
```typescript
interface Trade {
  id: number
  timestamp: number
  bot_id: string
  symbol: string
  side: 'long' | 'short'
  action: 'OPEN' | 'CLOSE'
  strategy: string
  price: number
  expected_price?: number
  slippage?: number
  size: number
  notional: number
  fee: number
  pnl?: number
  pnl_pct?: number
  reason: string
  stop_loss?: number
  take_profit?: number
}
```
- Sortable, filterable, paginated (20/page)
- Filters: Date range, Symbol, Side, Strategy, min PnL
- Expandable rows for full detail
- [Export CSV]

---

## Page 8: 🧪 Strategy Lab

This page is for browsing all available strategies, creating custom strategies, and viewing per-strategy performance.

### 8.1 StrategyBrowser

#### Built-in Strategies (read-only)
Current strategies registered in the backend:
- **ADX Trend** — Trend-following using ADX(14) + EMA crossover. Best in TRENDING regime.
- **Bollinger Bands** — Mean-reversion with BB(20,2σ) + RSI(14). Best in RANGING regime.
- **Breakout** — Donchian channel breakout (20-period). Best post-consolidation.
- **EMA Volume** — EMA(9)/EMA(21) crossover confirmed by volume spike. Best in TRENDING.
- **Z-Score** — Statistical mean-reversion using z-score(20). Best in RANGING.

Each strategy card shows:
- Name + description
- Regime affinity badge (TRENDING / RANGING / VOLATILE)
- Historical backtest summary (if available): win rate, Sharpe, avg trade
- Status: Active on N bots / Inactive
- [View Details] → parameters, logic description, indicator list

#### Custom Strategies (user-created, CRUD)
- [+ New Custom Strategy] button → opens StrategyEditor
- List of saved custom strategies
- Each shows: name, description, created date, backtest results
- Actions: [Edit] [Duplicate] [Backtest] [Delete]

### 8.2 StrategyEditor (drawer or full page)
Form for creating/editing a custom strategy:
```typescript
interface CustomStrategy {
  name: string                    // user-defined name
  description: string
  regime_affinity: 'trending' | 'ranging' | 'volatile' | 'all'

  // Entry conditions (combine with AND/OR)
  entry_long: IndicatorCondition[]
  entry_short: IndicatorCondition[]

  // Exit conditions
  exit_long: IndicatorCondition[]
  exit_short: IndicatorCondition[]

  // Risk overrides (optional)
  stop_loss_atr_mult?: number
  take_profit_atr_mult?: number
  min_bars_between_entries?: number

  // Indicator parameters
  indicators: IndicatorConfig[]
}

interface IndicatorCondition {
  indicator: string              // e.g. "RSI", "EMA", "MACD_SIGNAL"
  operator: '>' | '<' | '>=' | '<=' | 'crosses_above' | 'crosses_below'
  value: number | string         // number or another indicator name
}

interface IndicatorConfig {
  function: string               // TA-Lib function name
  params: Record<string, number> // e.g. { timeperiod: 14 }
  output_name: string           // alias used in conditions
}
```

The indicator selector should list **all TA-Lib functions** grouped by category:

#### Available TA-Lib Indicators

**Overlap Studies (17 functions)**
BBANDS, DEMA, EMA, HT_TRENDLINE, KAMA, MA, MAMA, MAVP, MIDPOINT, MIDPRICE, SAR, SAREXT, SMA, T3, TEMA, TRIMA, WMA

**Momentum Indicators (30 functions)**
ADX, ADXR, APO, AROON, AROONOSC, BOP, CCI, CMO, DX, MACD, MACDEXT, MACDFIX, MFI, MINUS_DI, MINUS_DM, MOM, PLUS_DI, PLUS_DM, PPO, ROC, ROCP, ROCR, ROCR100, RSI, STOCH, STOCHF, STOCHRSI, TRIX, ULTOSC, WILLR

**Volume Indicators (3 functions)**
AD, ADOSC, OBV

**Volatility Indicators (3 functions)**
ATR, NATR, TRANGE

**Price Transform (4 functions)**
AVGPRICE, MEDPRICE, TYPPRICE, WCLPRICE

**Cycle Indicators (5 functions)**
HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_TRENDMODE

**Pattern Recognition (61 functions)**
CDL2CROWS, CDL3BLACKCROWS, CDL3INSIDE, CDL3LINESTRIKE, CDL3STARSINSOUTH, CDL3WHITESOLDIERS, CDLABANDONEDBABY, CDLADVANCEBLOCK, CDLBELTHOLD, CDLBREAKAWAY, CDLCLOSINGMARUBOZU, CDLCONCEALBABYSWALL, CDLCOUNTERATTACK, CDLDARKCLOUDCOVER, CDLDOJI, CDLDOJISTAR, CDLDRAGONFLYDOJI, CDLENGULFING, CDLEVENINGDOJISTAR, CDLEVENINGSTAR, CDLGAPSIDESIDEWHITE, CDLGRAVESTONEDOJI, CDLHAMMER, CDLHANGINGMAN, CDLHARAMI, CDLHARAMICROSS, CDLHIGHWAVE, CDLHIKKAKE, CDLHIKKAKEMOD, CDLHOMINGPIGEON, CDLIDENTICAL3CROWS, CDLINNECK, CDLINVERTEDHAMMER, CDLKICKING, CDLKICKINGBYLENGTH, CDLLADDERBOTTOM, CDLLONGLEGGEDDOJI, CDLLONGLINE, CDLMARUBOZU, CDLMATCHINGLOW, CDLMATHOLD, CDLMORNINGDOJISTAR, CDLMORNINGSTAR, CDLONNECK, CDLPIERCING, CDLRICKSHAWMAN, CDLRISEFALL3METHODS, CDLSEPARATINGLINES, CDLSHOOTINGSTAR, CDLSHORTLINE, CDLSPINNINGTOP, CDLSTALLEDPATTERN, CDLSTICKSANDWICH, CDLTAKURI, CDLTASUKIGAP, CDLTHRUSTING, CDLTRISTAR, CDLUNIQUE3RIVER, CDLUPSIDEGAP2CROWS, CDLXSIDEGAP3METHODS

**Math Operators (11 functions)**
ADD, DIV, MAX, MAXINDEX, MIN, MININDEX, MINMAX, MINMAXINDEX, MULT, SUB, SUM

**Statistic Functions (9 functions)**
BETA, CORREL, LINEARREG, LINEARREG_ANGLE, LINEARREG_INTERCEPT, LINEARREG_SLOPE, STDDEV, TSF, VAR

The Strategy Editor UI should:
- Show a searchable grouped dropdown for indicator selection
- Auto-populate default parameters for each TA-Lib function
- Allow visual condition builder (drag-and-drop or form rows)
- Preview: show indicator output on a mini-chart with sample data
- [Save Strategy] persists via `POST /api/strategies`
- [Backtest This Strategy] sends to backtest page pre-filled

### 8.3 StrategyPerformanceComparison
- Table or chart comparing all strategies:
  - Win rate, Sharpe, Sortino, max DD, profit factor
  - Per regime: which strategy performs best in TRENDING vs RANGING vs VOLATILE
- Used by the auto-selection engine to pick strategies
- Help the user understand why the bot chose a particular strategy

---

## Page 9: ⚙️ Settings

This page consolidates all system configuration into tabbed sections.

### 9.1 Tabs Layout
```
[General] [Environment] [Risk Defaults] [Notifications] [Exchange] [System]
```

### 9.2 Tab: General
- **Paper/Live Mode**: Toggle switch with confirmation modal for Live
- **Default Timeframe**: 5m / 15m / 1h / 4h
- **Default Leverage**: Slider 1–10x
- **Default Position Size %**: Number input
- **Auto-Strategy Mode**: Toggle (globally enable/disable autonomous strategy selection)
- **Regime Detection Sensitivity**: Slider (ADX hysteresis thresholds)

### 9.3 Tab: Environment Variables
Edit `.env` variables from the UI. Fetch from `GET /api/env`, save via `PUT /api/env`.

```typescript
interface EnvVariable {
  key: string
  value: string
  masked: boolean        // true for secrets (show •••••)
  category: string       // grouping
  description: string    // helper text
  requires_restart: boolean
}
```

Display as grouped form:

**Binance API Credentials**
| Variable | Value | Description |
|----------|-------|-------------|
| BINANCE_API_KEY | •••••  [👁 Show] | Binance Futures API key |
| BINANCE_SECRET | ••••• [👁 Show] | Binance API secret |

**Database (Memgraph)**
| Variable | Value | Description |
|----------|-------|-------------|
| MEMGRAPH_HOST | memgraph | Memgraph hostname |
| MEMGRAPH_PORT | 7687 | Bolt protocol port |
| MEMGRAPH_USERNAME | (empty) | Auth username |
| MEMGRAPH_PASSWORD | ••••• | Auth password |

**Redis**
| Variable | Value | Description |
|----------|-------|-------------|
| REDIS_HOST | redis | Redis hostname |
| REDIS_PORT | 6379 | Redis port |

**Notifications**
| Variable | Value | Description |
|----------|-------|-------------|
| DISCORD_WEBHOOK_URL | https://disc... | Discord webhook for alerts |

**Security**
| Variable | Value | Description |
|----------|-------|-------------|
| OMNITRADER_API_KEY | ••••• | API auth key (required for mutations) |

Features:
- [Save Changes] button — writes to `.env` file via API
- Warning banner: "⚠️ Changes marked with 🔄 require a service restart"
- [Restart Services] button (with confirmation: "This will restart all Docker containers")
- Secret values masked by default, click eye icon to reveal
- Validation: warn if BINANCE_API_KEY is empty and mode is Live

### 9.4 Tab: Risk Defaults
- Max daily loss %
- Max weekly loss %
- Consecutive loss limit
- Stop loss mode: Fixed % / ATR multiplier
- Take profit mode: Fixed % / ATR multiplier
- Trailing stop config (activation %, callback %)
- Black swan threshold (% move in 1h)
- Auto-deleverage trigger (drawdown %)

### 9.5 Tab: Notifications
- Discord webhook URL (masked input + [Test] button)
- Checkboxes: Trade executions, Circuit breakers, Daily summaries, Errors, Strategy rotations
- Notification cooldown (min seconds between messages)

### 9.6 Tab: Exchange
- Exchange adapter selector: "Binance Direct" / "CCXT" / "Auto-fallback"
- Connection test button + latency display
- Adapter health metrics (success rate, avg latency, errors)
- Rate limit monitor (current usage / limit)

### 9.7 Tab: System
- Docker service status (list all containers from compose.yml with status)
- Memgraph connection status + node/relationship counts
- Redis connection status + memory usage
- Ollama status + loaded model
- [Backup Database] button
- [View Logs] → opens log viewer modal (tail last 100 lines of omnitrader container)
- Version info

---

## Shared Components

```typescript
// StatCard — single metric display
interface StatCardProps {
  label: string
  value: string | number
  trend?: 'up' | 'down' | 'neutral'
  color?: 'green' | 'red' | 'accent' | 'yellow'
  suffix?: string
  prefix?: string
}

// Badge — status pills
interface BadgeProps {
  children: React.ReactNode
  variant: 'success' | 'danger' | 'warning' | 'info' | 'neutral'
  pulse?: boolean           // animated pulse for active states
  size?: 'sm' | 'md'
}

// Panel — container card
interface PanelProps {
  title?: string
  subtitle?: string
  children: React.ReactNode
  actions?: React.ReactNode
  collapsible?: boolean
}

// Button
interface ButtonProps {
  variant: 'primary' | 'success' | 'danger' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: React.ReactNode
}

// SentimentEmoji — emoji face scaled by score
// -1.0 → 😢, -0.5 → 😟, 0 → 😐, +0.5 → 🙂, +1.0 → 😊

// ProgressBar — horizontal bar with color thresholds
// Modal — confirmation / info dialogs
// Drawer — slide-in side panels (right side)
// Toast — top-right notification toasts (success, error, info)
// LoadingSpinner — animated spinner
// EmptyState — placeholder with icon + message + action button
// DataTable — TanStack Table wrapper (sort, filter, paginate, export)
// SearchableSelect — dropdown with type-to-search + grouping
```

---

## WebSocket Manager

```typescript
// lib/ws.ts — exponential backoff reconnection
export function useLiveFeed() {
  // Manages WS connection to ws://localhost:8000/ws
  // Dispatches messages by type: 'cycle_update' | 'alert' | 'trade'
  // Returns: { botUpdates: Map<string, CycleMessage>, alerts: AlertMessage[], trades: TradeMessage[], status }
  // Auto-reconnect with backoff: 1s, 2s, 4s, 8s, max 30s
  // Show toast on reconnect
}
```

---

## API Client

```typescript
// lib/api.ts — typed fetch wrappers
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Bots
fetchBots(): Promise<Bot[]>
createBot(config): Promise<Bot>
updateBot(id, config): Promise<Bot>
deleteBot(id): Promise<void>
startBot(id): Promise<void>
stopBot(id): Promise<void>

// Strategies
fetchStrategies(): Promise<Strategy[]>
saveStrategy(strategy): Promise<Strategy>
deleteStrategy(name): Promise<void>

// Analytics
fetchTradeHistory(filters): Promise<{ trades: Trade[], total: number }>
fetchEquitySnapshots(symbol?, days?): Promise<EquitySnapshot[]>

// Intelligence
fetchSentiment(symbol): Promise<SentimentData>
fetchCrisisStatus(): Promise<CrisisStatus>
toggleCrisisMode(active): Promise<void>
fetchNews(): Promise<NewsItem[]>

// Backtest
runBacktest(config): Promise<{ id: string }>
fetchBacktestResults(id): Promise<BacktestResults>

// Config
fetchConfig(): Promise<Config>
updateConfig(config): Promise<Config>

// Env
fetchEnvVars(): Promise<EnvVariable[]>
updateEnvVars(vars): Promise<{ requires_restart: boolean }>

// Markets
fetchMarkets(): Promise<MarketPair[]>
```

---

## Responsive Design

- **Desktop** (≥1280px): Full sidebar + multi-column grids
- **Tablet** (768–1279px): Sidebar collapses to icons only, 2-column grids
- **Mobile** (<768px): Sidebar becomes bottom tab bar (top 5 items), single column, cards stack

---

## Loading, Error & Empty States

Every data component handles:
1. **Loading**: Skeleton placeholders matching layout shape
2. **Error**: Red banner with message + [Retry] button
3. **Empty**: EmptyState: icon + text + optional action (e.g. "No bots yet" → [Create First Bot])

---

## Key Interactions

1. **Toast notifications** on trade events, errors, config saves
2. **Confirmation modals** for: Stop Bot, Delete Bot, Delete Strategy, Switch to Live Mode, Restart Services, Change Env Vars
3. **WebSocket reconnection** toast: "Reconnecting..." → "Connected"
4. **Form validation** inline with red borders + error text
5. **Optimistic updates** on bot start/stop, config save
6. **Keyboard shortcuts**: Escape closes drawers/modals, Enter confirms

---

## Must-Have vs Nice-to-Have

### MUST HAVE (Ship-blocking)
- Multi-asset bot management (create, start, stop, delete bots per symbol)
- Autonomous strategy selection (bot auto-picks based on regime)
- Real-time WebSocket updates per bot
- Environment variable editor in Settings
- Strategy Lab with all TA-Lib indicators for custom strategy creation
- Save/load custom strategies
- Risk monitor with circuit breakers
- Trade history with filters and export
- Basic equity curve chart
- Crisis mode toggle
- Responsive layout (desktop + mobile)

### SHOULD HAVE (Important but not blocking)
- Backtesting page with full metrics
- News feed from knowledge graph
- Candlestick chart with signal overlay
- Strategy performance comparison table
- Macro indicators panel (Fear/Greed, DXY, Oil, BTC.D)
- Docker service status in Settings
- Walk-forward and bootstrap CI displays

### NICE TO HAVE (Polish, ship later)
- Drag-and-drop strategy condition builder
- Correlation matrix heatmap
- Monthly returns heatmap
- SMC analysis panel
- Semi-automatic approval queue
- Log viewer in Settings
- Dark/light theme toggle
- Export equity curve as PNG

---

## Success Criteria

✅ Multi-asset: user can run bots on BTC, ETH, SOL, or any Binance pair simultaneously
✅ Auto-strategy: bots autonomously pick and rotate strategies per regime
✅ Custom strategies: user can create, save, edit strategies using any TA-Lib indicator
✅ Env editor: user can view and modify .env variables from Settings page
✅ All 9 pages functional with real-time data
✅ Dark theme consistent everywhere
✅ Responsive on desktop and mobile
✅ All critical API integrations working
✅ Error handling and loading states on all async components

Generate the complete application following this specification.
