// ===== Bot & Position Types =====
export interface Position {
  side: 'long' | 'short';
  entry_price: number;
  size: number;
  unrealized_pnl: number;
  stop_loss: number;
  take_profit: number;
  opened_at: number;
}

export interface Bot {
  id: string;
  symbol: string;
  status: 'running' | 'stopped' | 'paused' | 'error';
  mode: 'auto' | 'manual';
  active_strategy: string;
  regime: 'trending' | 'ranging' | 'volatile';
  position: Position | null;
  daily_pnl: number;
  daily_pnl_pct: number;
  balance_allocated: number;
  leverage: number;
  created_at: number;
}

// ===== WebSocket Message Types =====
export interface CycleMessage {
  type: 'cycle_update';
  bot_id: string;
  symbol: string;
  timestamp: number;
  price: number;
  signal: 'LONG' | 'SHORT' | 'HOLD' | 'EXIT_LONG' | 'EXIT_SHORT';
  active_strategy: string;
  regime: 'trending' | 'ranging' | 'volatile';
  position: 'long' | 'short' | null;
  balance: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  circuit_breaker: boolean;
  reason?: string;
  sentiment?: number;
  crisis_mode?: boolean;
  macro_indicators?: {
    fear_greed: number;
    dxy: number;
    oil: number;
    btc_dominance: number;
  };
  divergence_flag?: boolean;
}

export interface AlertMessage {
  type: 'alert';
  level: 'info' | 'warning' | 'critical';
  title: string;
  body: string;
  timestamp: number;
}

export interface TradeMessage {
  type: 'trade';
  bot_id: string;
  symbol: string;
  action: 'OPEN' | 'CLOSE';
  side: 'long' | 'short';
  price: number;
  size: number;
  pnl?: number;
  strategy: string;
  timestamp: number;
}

// ===== Trade History =====
export interface Trade {
  id: number;
  timestamp: number;
  bot_id: string;
  symbol: string;
  side: 'long' | 'short';
  action: 'OPEN' | 'CLOSE';
  strategy: string;
  price: number;
  expected_price?: number;
  slippage?: number;
  size: number;
  notional: number;
  fee: number;
  pnl?: number;
  pnl_pct?: number;
  reason: string;
  stop_loss?: number;
  take_profit?: number;
}

// ===== Strategy =====
export interface Strategy {
  name: string;
  description: string;
  regime_affinity: 'trending' | 'ranging' | 'volatile' | 'all';
  builtin: boolean;
  win_rate?: number;
  sharpe?: number;
  avg_trade?: number;
  active_bots?: number;
  indicators?: IndicatorConfig[];
  entry_long?: IndicatorCondition[];
  entry_short?: IndicatorCondition[];
  exit_long?: IndicatorCondition[];
  exit_short?: IndicatorCondition[];
  stop_loss_atr_mult?: number;
  take_profit_atr_mult?: number;
  min_bars_between_entries?: number;
}

export interface IndicatorCondition {
  indicator: string;
  operator: '>' | '<' | '>=' | '<=' | 'crosses_above' | 'crosses_below';
  value: number | string;
}

export interface IndicatorConfig {
  function: string;
  params: Record<string, number>;
  output_name: string;
}

// ===== Backtest =====
export interface BacktestConfig {
  symbol: string;
  start_date: string;
  end_date: string;
  strategy: string;
  timeframe: string;
  initial_capital: number;
  position_size_pct: number;
  leverage: number;
}

export interface BacktestResults {
  id: string;
  config: BacktestConfig;
  total_pnl: number;
  total_return_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown_pct: number;
  profit_factor: number;
  win_rate_pct: number;
  avg_win_loss_ratio: number;
  total_trades: number;
  wins: number;
  losses: number;
  avg_trade_duration_hours: number;
  best_trade_pnl: number;
  worst_trade_pnl: number;
  equity_curve: { timestamp: number; equity: number; drawdown: number }[];
  monthly_returns: { year: number; month: number; return_pct: number }[];
  trades: Trade[];
}

// ===== Intelligence =====
export interface NewsItem {
  id: string;
  title: string;
  source: string;
  published_at: number;
  sentiment_score: number;
  impact_level: number;
  assets: string[];
  sectors: string[];
}

export interface SentimentData {
  score: number;
  label: string;
  article_count: number;
  max_impact: number;
}

export interface CrisisStatus {
  active: boolean;
  source: 'auto' | 'manual';
  triggered_at?: number;
}

// ===== Config =====
export interface EnvVariable {
  key: string;
  value: string;
  masked: boolean;
  category: string;
  description: string;
  requires_restart: boolean;
}

export interface AppConfig {
  mode: 'paper' | 'live';
  default_timeframe: string;
  default_leverage: number;
  default_position_size_pct: number;
  auto_strategy_mode: boolean;
  regime_sensitivity: number;
  max_daily_loss_pct: number;
  max_weekly_loss_pct: number;
  consecutive_loss_limit: number;
  stop_loss_mode: 'fixed' | 'atr';
  stop_loss_value: number;
  take_profit_mode: 'fixed' | 'atr';
  take_profit_value: number;
  trailing_stop_activation_pct: number;
  trailing_stop_callback_pct: number;
  black_swan_threshold: number;
  auto_deleverage_drawdown_pct: number;
  discord_webhook_url: string;
  notify_trades: boolean;
  notify_circuit_breakers: boolean;
  notify_daily_summary: boolean;
  notify_errors: boolean;
  notify_strategy_rotations: boolean;
  notification_cooldown_secs: number;
  exchange_adapter: 'binance' | 'ccxt' | 'auto';
}

export interface MarketPair {
  symbol: string;
  base: string;
  quote: string;
  volume_24h: number;
  last_price: number;
}

export interface EquitySnapshot {
  timestamp: number;
  equity: number;
  bot_id?: string;
  symbol?: string;
}

// ===== Circuit Breaker =====
export interface CircuitBreaker {
  name: string;
  limit: string;
  current: string;
  current_pct: number;
  status: 'ok' | 'warning' | 'triggered';
}
