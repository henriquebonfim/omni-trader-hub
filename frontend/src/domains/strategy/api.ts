import { request } from '@/core/api';
import { adaptStrategy } from '@/lib/adapters';
import type { Strategy, StrategyPerformanceEntry } from './types';

export const fetchStrategies = async () => {
  try {
    const data = await request<{ strategies: Record<string, unknown>[]; active: string }>('/api/strategies');
    return data.strategies.map(adaptStrategy);
  } catch (e) {
    console.error('fetchStrategies error', e);
    return [];
  }
};

export const fetchStrategyPerformance = async () => {
  const data = await request<{ performance: Record<string, Array<Record<string, unknown>>> }>('/api/strategies/performance');
  return Object.entries(data.performance).flatMap(([regime, rows]) =>
    rows.map((row) => ({
      name: String(row.name ?? ''),
      regime: regime as StrategyPerformanceEntry['regime'],
      sample_size: Number(row.sample_size ?? 0),
      sharpe: Number(row.sharpe ?? 0),
      profit_factor: Number(row.profit_factor ?? 0),
      win_rate: Number(row.win_rate ?? 0),
      composite_score: Number(row.composite_score ?? 0),
    }))
  );
};

export const saveStrategy = (strategy: Partial<Strategy>) =>
  request<Strategy>('/api/strategies', { method: 'POST', body: JSON.stringify(strategy) });
export const updateStrategy = (name: string, strategy: Partial<Strategy>) =>
  request<Strategy>(`/api/strategies/${name}`, { method: 'PUT', body: JSON.stringify(strategy) });
export const deleteStrategy = (name: string) =>
  request<void>(`/api/strategies/${name}`, { method: 'DELETE' });
