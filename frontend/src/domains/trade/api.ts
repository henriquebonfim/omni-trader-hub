import { request } from '@/core/api';
import type { Trade, BacktestConfig, BacktestResults, EquitySnapshot } from './types';

export const fetchTradeHistory = (filters?: Record<string, string>) => {
  const params = new URLSearchParams(filters);
  return request<{ trades: Trade[]; total: number }>(`/api/trades/history?${params}`);
};
export const fetchEquitySnapshots = (symbol?: string, days?: number) => {
  const params = new URLSearchParams();
  if (symbol) params.set('symbol', symbol);
  if (days) params.set('days', String(days));
  return request<EquitySnapshot[]>(`/api/equity/snapshots?${params}`);
};

export const runBacktest = (config: BacktestConfig) =>
  request<{ id: string }>('/api/backtest/run', { method: 'POST', body: JSON.stringify(config) });
export const fetchBacktestResults = (id: string) =>
  request<BacktestResults>(`/api/backtest/results/${id}`);
