import type { Bot } from './types';

export const mockBots: Bot[] = [
  {
    id: 'bot-1', symbol: 'BTC/USDT', status: 'running', mode: 'auto',
    active_strategy: 'ADX Trend', regime: 'trending',
    position: { side: 'long', entry_price: 67250, size: 0.15, unrealized_pnl: 312.50, stop_loss: 65800, take_profit: 70000, opened_at: Date.now() - 3600000 },
    daily_pnl: 485.20, daily_pnl_pct: 2.42, balance_allocated: 20000, leverage: 3, created_at: Date.now() - 86400000 * 7,
  },
  {
    id: 'bot-2', symbol: 'ETH/USDT', status: 'running', mode: 'auto',
    active_strategy: 'Bollinger Bands', regime: 'ranging',
    position: null,
    daily_pnl: 123.80, daily_pnl_pct: 0.83, balance_allocated: 15000, leverage: 3, created_at: Date.now() - 86400000 * 5,
  },
  {
    id: 'bot-3', symbol: 'SOL/USDT', status: 'running', mode: 'manual',
    active_strategy: 'Breakout', regime: 'volatile',
    position: { side: 'short', entry_price: 178.50, size: 100, unrealized_pnl: -45.00, stop_loss: 185.00, take_profit: 165.00, opened_at: Date.now() - 1800000 },
    daily_pnl: -89.30, daily_pnl_pct: -0.89, balance_allocated: 10000, leverage: 5, created_at: Date.now() - 86400000 * 3,
  },
  {
    id: 'bot-4', symbol: 'DOGE/USDT', status: 'paused', mode: 'auto',
    active_strategy: 'EMA Volume', regime: 'trending',
    position: null,
    daily_pnl: 0, daily_pnl_pct: 0, balance_allocated: 5000, leverage: 2, created_at: Date.now() - 86400000 * 10,
  },
  {
    id: 'bot-5', symbol: 'AVAX/USDT', status: 'stopped', mode: 'auto',
    active_strategy: '', regime: 'ranging',
    position: null,
    daily_pnl: 0, daily_pnl_pct: 0, balance_allocated: 8000, leverage: 3, created_at: Date.now() - 86400000 * 14,
  },
];
