import { request } from '@/core/api';
import type { Bot } from './types';

export const fetchBots = () => request<Bot[]>('/api/bots');
export const createBot = (config: Partial<Bot>) =>
  request<Bot>('/api/bots', { method: 'POST', body: JSON.stringify(config) });
export const updateBot = (id: string, config: Partial<Bot>) =>
  request<Bot>(`/api/bots/${id}`, { method: 'PUT', body: JSON.stringify(config) });
export const deleteBot = (id: string) =>
  request<void>(`/api/bots/${id}`, { method: 'DELETE' });
export const startBot = (id: string) =>
  request<void>(`/api/bots/${id}/start`, { method: 'POST' });
export const stopBot = (id: string) =>
  request<void>(`/api/bots/${id}/stop`, { method: 'POST' });
