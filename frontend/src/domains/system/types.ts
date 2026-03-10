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

export interface CrisisStatus {
  active: boolean;
  source: 'auto' | 'manual';
  triggered_at?: number;
}

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
