import { request } from '@/core/api';
import type { Strategy } from './types';

export const fetchStrategies = () => request<Strategy[]>('/api/strategies');
export const saveStrategy = (strategy: Partial<Strategy>) =>
  request<Strategy>('/api/strategies', { method: 'POST', body: JSON.stringify(strategy) });
export const updateStrategy = (name: string, strategy: Partial<Strategy>) =>
  request<Strategy>(`/api/strategies/${name}`, { method: 'PUT', body: JSON.stringify(strategy) });
export const deleteStrategy = (name: string) =>
  request<void>(`/api/strategies/${name}`, { method: 'DELETE' });
