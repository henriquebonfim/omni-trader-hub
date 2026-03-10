import { request } from '@/core/api';
import type { AppConfig, EnvVariable } from './types';

export const fetchConfig = () => request<AppConfig>('/api/config');
export const updateConfig = (config: Partial<AppConfig>) =>
  request<AppConfig>('/api/config', { method: 'PUT', body: JSON.stringify(config) });

export const fetchEnvVars = () => request<EnvVariable[]>('/api/env');
export const updateEnvVars = (vars: EnvVariable[]) =>
  request<{ requires_restart: boolean }>('/api/env', { method: 'PUT', body: JSON.stringify(vars) });
