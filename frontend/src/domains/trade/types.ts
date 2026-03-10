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

export interface EquitySnapshot {
  timestamp: number;
  equity: number;
  bot_id?: string;
  symbol?: string;
}
