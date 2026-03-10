import type { Strategy } from './types';

export const mockStrategies: Strategy[] = [
  { name: 'ADX Trend', description: 'Trend-following using ADX(14) + EMA crossover. Best in TRENDING regime.', regime_affinity: 'trending', builtin: true, win_rate: 52, sharpe: 1.8, avg_trade: 1.2, active_bots: 2 },
  { name: 'Bollinger Bands', description: 'Mean-reversion with BB(20,2σ) + RSI(14). Best in RANGING regime.', regime_affinity: 'ranging', builtin: true, win_rate: 58, sharpe: 1.4, avg_trade: 0.8, active_bots: 1 },
  { name: 'Breakout', description: 'Donchian channel breakout (20-period). Best post-consolidation.', regime_affinity: 'volatile', builtin: true, win_rate: 45, sharpe: 1.6, avg_trade: 1.5, active_bots: 1 },
  { name: 'EMA Volume', description: 'EMA(9)/EMA(21) crossover confirmed by volume spike. Best in TRENDING.', regime_affinity: 'trending', builtin: true, win_rate: 50, sharpe: 1.3, avg_trade: 0.9, active_bots: 1 },
  { name: 'Z-Score', description: 'Statistical mean-reversion using z-score(20). Best in RANGING.', regime_affinity: 'ranging', builtin: true, win_rate: 55, sharpe: 1.5, avg_trade: 0.7, active_bots: 0 },
];
