import { request } from '@/core/api';
import { adaptEquitySnapshot, adaptTrade } from '@/lib/adapters';
import { stubBacktestResults } from '@/lib/stubs';
import type { BacktestConfig, BacktestResults } from './types';

export const fetchTradeHistory = async (filters?: Record<string, string>) => {
  const params = new URLSearchParams(filters);
  try {
    const res = await request<{ trades: Record<string, unknown>[]; count: number }>(`/api/trades?${params}`);
    return { trades: res.trades.map(adaptTrade), total: res.count };
  } catch (e) {
    console.error('fetchTradeHistory error', e);
    return { trades: [], total: 0 };
  }
};

export const fetchEquitySnapshots = async (symbol?: string, days?: number) => {
  const params = new URLSearchParams();
  if (symbol) params.set('symbol', symbol);
  if (days) params.set('days', String(days));
  try {
    const res = await request<{ snapshots: Record<string, unknown>[]; count: number }>(`/api/equity?${params}`);
    return res.snapshots.map(adaptEquitySnapshot);
  } catch (e) {
    console.error('fetchEquitySnapshots error', e);
    return [];
  }
};

export const runBacktest = async (config: BacktestConfig) => {
  try {
    return await request<{ id: string }>('/api/backtest/run', { method: 'POST', body: JSON.stringify(config) });
  } catch (e) {
    console.warn('runBacktest stubbed', e);
    return { id: 'bt-1' };
  }
};
export const fetchBacktestResults = async (id: string) => {
  try {
    return await request<BacktestResults>(`/api/backtest/results/${id}`);
  } catch (e) {
    console.warn('fetchBacktestResults stubbed', e);
    return stubBacktestResults();
  }
};
