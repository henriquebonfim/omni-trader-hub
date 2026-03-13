import { request } from '@/core/api';
import { adaptConfig, reverseAdaptConfig } from '@/lib/adapters';
import { stubEnvVars } from '@/lib/stubs';
import type { AppConfig, EnvVariable, NotificationRules } from './types';

interface DiscordWebhookState {
  enabled: boolean;
  configured: boolean;
  webhook_url_preview: string;
}

export const fetchConfig = async () => {
  try {
    const data = await request<Record<string, unknown>>('/api/config');
    return adaptConfig(data);
  } catch (e) {
    console.error('fetchConfig error', e);
    throw e;
  }
};
export const updateConfig = async (config: AppConfig) => {
  try {
    const reversed = reverseAdaptConfig(config);
    await request<Record<string, unknown>>('/api/config', { method: 'PUT', body: JSON.stringify(reversed) });
    return config;
  } catch (e) {
    console.error('updateConfig error', e);
    throw e;
  }
};

export const fetchEnvVars = async () => {
  try {
    const raw = await request<Record<string, Record<string, { value: string; masked: boolean; description: string; requires_restart: boolean }>>>('/api/env');
    const vars: EnvVariable[] = [];
    for (const [category, entries] of Object.entries(raw)) {
      for (const [key, meta] of Object.entries(entries)) {
        vars.push({ key, value: meta.value, masked: meta.masked, category, description: meta.description, requires_restart: meta.requires_restart });
      }
    }
    return vars;
  } catch (e) {
    console.warn('fetchEnvVars stubbed', e);
    return stubEnvVars();
  }
};
export const updateEnvVars = async (vars: EnvVariable[]) => {
  try {
    const payload = Object.fromEntries(vars.map(v => [v.key, v.value]));
    return await request<{ requires_restart: boolean }>('/api/env', { method: 'PUT', body: JSON.stringify(payload) });
  } catch (e) {
    console.warn('updateEnvVars stubbed', e);
    return { requires_restart: true };
  }
};

export const fetchNotificationRules = async () => {
  try {
    return await request<NotificationRules>('/api/notifications/rules');
  } catch (e) {
    console.error('fetchNotificationRules error', e);
    throw e;
  }
};

export const updateNotificationRules = async (rules: NotificationRules) => {
  try {
    return await request<{ ok: boolean; rules: NotificationRules }>('/api/notifications/rules', {
      method: 'PUT',
      body: JSON.stringify(rules),
    });
  } catch (e) {
    console.error('updateNotificationRules error', e);
    throw e;
  }
};

export const fetchDiscordWebhook = async () => {
  return request<DiscordWebhookState>('/api/notifications/discord');
};

export const updateDiscordWebhook = (url: string) =>
  request<{ ok: boolean }>('/api/notifications/discord', { method: 'PUT', body: JSON.stringify({ webhook_url: url }) });

export const testDiscordWebhook = () =>
  request<{ ok: boolean; message: string }>('/api/notifications/discord/test', { method: 'POST' });

export const restartSystem = (force = false) =>
  request<{ ok: boolean; message: string }>('/api/system/restart', {
    method: 'POST',
    body: JSON.stringify({ confirm: true, force }),
  });

export interface SystemInfo {
  uptime_seconds: number;
  node_count: number;
  relationship_count: number;
  rate_limit_used: number;
  rate_limit_capacity: number;
  ollama_model: string;
  version: string;
  services: Record<string, string>;
}

export const fetchSystemInfo = async (): Promise<SystemInfo> => {
  return request<SystemInfo>('/api/system/info');
};

export const backupDatabase = async () =>
  request<{ ok: boolean; timestamp: string }>('/api/system/backup', { method: 'POST' });

export const fetchStatusSummary = async () =>
  request<{
    running: boolean;
    running_count?: number;
    total_bots?: number;
    uptime_seconds: number;
    circuit_breaker_active: boolean;
    ws_clients: number;
  }>('/api/status');
