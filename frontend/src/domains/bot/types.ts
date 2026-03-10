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
