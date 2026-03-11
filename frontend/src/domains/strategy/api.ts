import { request } from '@/core/api';
import { adaptStrategy } from '@/lib/adapters';
import type { Strategy } from './types';

export const fetchStrategies = async () => {
  try {
    const data = await request<Record<string, unknown>[]>('/api/strategies');
    return data.map(adaptStrategy);
  } catch (e) {
    console.error('fetchStrategies error', e);
    return [];
  }
};
export const saveStrategy = (strategy: Partial<Strategy>) =>
  request<Strategy>('/api/strategies', { method: 'POST', body: JSON.stringify(strategy) });
export const updateStrategy = (name: string, strategy: Partial<Strategy>) =>
  request<Strategy>(`/api/strategies/${name}`, { method: 'PUT', body: JSON.stringify(strategy) });
export const deleteStrategy = (name: string) =>
  request<void>(`/api/strategies/${name}`, { method: 'DELETE' });
