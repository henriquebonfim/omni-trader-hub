import type { Trade, BacktestResults, EquitySnapshot } from './types';
import { mockBots } from '@/domains/bot/mocks';

export const mockTrades: Trade[] = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  timestamp: Date.now() - i * 3600000 * 2,
  bot_id: mockBots[i % 3].id,
  symbol: mockBots[i % 3].symbol,
  side: i % 2 === 0 ? 'long' as const : 'short' as const,
  action: i % 4 === 0 ? 'OPEN' as const : 'CLOSE' as const,
  strategy: ['ADX Trend', 'Bollinger Bands', 'Breakout', 'EMA Volume'][i % 4],
  price: 67000 + Math.random() * 1000,
  size: 0.1 + Math.random() * 0.2,
  notional: 6700 + Math.random() * 200,
  fee: 2.5 + Math.random() * 1.5,
  pnl: i % 4 !== 0 ? (Math.random() - 0.4) * 200 : undefined,
  pnl_pct: i % 4 !== 0 ? (Math.random() - 0.4) * 3 : undefined,
  reason: ['Signal: LONG', 'Signal: EXIT_LONG', 'Stop Loss Hit', 'Take Profit Hit'][i % 4],
}));

export const mockBacktestResults: BacktestResults = {
  id: 'bt-1',
  config: { symbol: 'BTC/USDT', start_date: '2024-01-01', end_date: '2024-06-30', strategy: 'ADX Trend', timeframe: '1h', initial_capital: 10000, position_size_pct: 5, leverage: 3 },
  total_pnl: 3245.80, total_return_pct: 32.46, sharpe_ratio: 1.82, sortino_ratio: 2.15,
  max_drawdown_pct: 8.3, profit_factor: 1.85, win_rate_pct: 54.2, avg_win_loss_ratio: 1.68,
  total_trades: 142, wins: 77, losses: 65, avg_trade_duration_hours: 4.2,
  best_trade_pnl: 892.50, worst_trade_pnl: -312.40,
  equity_curve: Array.from({ length: 180 }, (_, i) => ({
    timestamp: new Date('2024-01-01').getTime() + i * 86400000,
    equity: 10000 + i * 18 + Math.sin(i * 0.15) * 400 + Math.random() * 100,
    drawdown: Math.max(0, Math.sin(i * 0.1) * 5 + Math.random() * 2),
  })),
  monthly_returns: [
    { year: 2024, month: 1, return_pct: 5.2 }, { year: 2024, month: 2, return_pct: 8.1 },
    { year: 2024, month: 3, return_pct: -2.3 }, { year: 2024, month: 4, return_pct: 6.8 },
    { year: 2024, month: 5, return_pct: 11.4 }, { year: 2024, month: 6, return_pct: 3.2 },
  ],
  trades: mockTrades.slice(0, 20),
};

export const mockEquitySnapshots: EquitySnapshot[] = Array.from({ length: 90 }, (_, i) => ({
  timestamp: Date.now() - (89 - i) * 86400000,
  equity: 50000 + i * 120 + Math.sin(i * 0.3) * 800 + Math.random() * 300,
}));
