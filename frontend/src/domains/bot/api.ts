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

export const restartBot = async (id: string, force: boolean = false) => {
  if (id === 'default') return request<void>('/api/bot/restart', { method: 'POST', body: JSON.stringify({ confirm: true, force }) });
  // For multi-bot, we don't have a direct restart route, so we stop then start
  await stopBot(id);
  return startBot(id);
};

export const manualOpenTrade = async (id: string, side: 'long' | 'short') => {
  if (id === 'default') return request<void>('/api/bot/trade/open', { method: 'POST', body: JSON.stringify({ side }) });
  return request<void>(`/api/bots/${id}/trade/open`, { method: 'POST', body: JSON.stringify({ side }) });
};

export const manualCloseTrade = async (id: string) => {
  if (id === 'default') return request<void>('/api/bot/trade/close', { method: 'POST' });
  return request<void>(`/api/bots/${id}/trade/close`, { method: 'POST' });
};

export const fetchBotState = async (id: string) => {
  if (id === 'default') return request<Record<string, unknown>>('/api/bot/state');
  return request<Record<string, unknown>>(`/api/bots/${id}`);
};
