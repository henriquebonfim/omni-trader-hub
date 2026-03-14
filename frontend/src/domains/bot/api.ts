import { request } from '@/core/api';
import { adaptBot } from '@/lib/adapters';
import type { Bot } from './types';

export const fetchBots = async () => {
  try {
    const bots = await request<Record<string, unknown>[]>('/api/bots');
    return (bots || []).map(adaptBot);
  } catch (e) {
    console.error('fetchBots error', e);
    return [];
  }
};

export const createBot = (config: Partial<Bot>) =>
  request<{ ok: boolean; bot_id: string }>('/api/bots', { method: 'POST', body: JSON.stringify({ config }) });
export const updateBot = (id: string, config: Partial<Bot>) =>
  request<Bot>(`/api/bots/${id}`, { method: 'PUT', body: JSON.stringify({ config }) });
export const deleteBot = (id: string) =>
  request<void>(`/api/bots/${id}`, { method: 'DELETE' });
export const startBot = async (id: string) => {
  if (id === 'default') return request<void>('/api/bot/start', { method: 'POST' });
  return request<void>(`/api/bots/${id}/start`, { method: 'POST' });
};
export const stopBot = async (id: string) => {
  if (id === 'default') return request<void>('/api/bot/stop?confirm=true', { method: 'POST' });
  return request<void>(`/api/bots/${id}/stop?confirm=true`, { method: 'POST' });
};
