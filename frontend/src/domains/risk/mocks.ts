import type { CircuitBreaker } from './types';

export const mockCircuitBreakers: CircuitBreaker[] = [
  { name: 'Daily Loss', limit: '-5%', current: '-1.2%', current_pct: 24, status: 'ok' },
  { name: 'Consecutive Losses', limit: '3 max', current: '1', current_pct: 33, status: 'ok' },
  { name: 'Weekly Loss', limit: '-10%', current: '-3.5%', current_pct: 35, status: 'ok' },
  { name: 'Black Swan', limit: '>10% move', current: '2.1%', current_pct: 21, status: 'ok' },
  { name: 'Volatility Spike', limit: '>3× ATR', current: '1.8×', current_pct: 60, status: 'warning' },
];
