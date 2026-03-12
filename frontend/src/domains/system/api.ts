import { request } from '@/core/api';
import { adaptConfig, reverseAdaptConfig } from '@/lib/adapters';
import { stubEnvVars } from '@/lib/stubs';
import type { AppConfig, EnvVariable, NotificationRules } from './types';

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
    return await request<EnvVariable[]>('/api/env');
  } catch (e) {
    console.warn('fetchEnvVars stubbed', e);
    return stubEnvVars();
  }
};
export const updateEnvVars = async (vars: EnvVariable[]) => {
  try {
    return await request<{ requires_restart: boolean }>('/api/env', { method: 'PUT', body: JSON.stringify(vars) });
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
