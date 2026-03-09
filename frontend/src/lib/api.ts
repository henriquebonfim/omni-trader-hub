import type {
  Bot, Trade, Strategy, BacktestConfig, BacktestResults,
  SentimentData, CrisisStatus, NewsItem, AppConfig,
  EnvVariable, MarketPair, EquitySnapshot
} from '@/types';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error: ${res.status} ${res.statusText}`);
  return res.json();
}

// Bots
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

// Strategies
export const fetchStrategies = () => request<Strategy[]>('/api/strategies');
export const saveStrategy = (strategy: Partial<Strategy>) =>
  request<Strategy>('/api/strategies', { method: 'POST', body: JSON.stringify(strategy) });
export const updateStrategy = (name: string, strategy: Partial<Strategy>) =>
  request<Strategy>(`/api/strategies/${name}`, { method: 'PUT', body: JSON.stringify(strategy) });
export const deleteStrategy = (name: string) =>
  request<void>(`/api/strategies/${name}`, { method: 'DELETE' });

// Analytics
export const fetchTradeHistory = (filters?: Record<string, string>) => {
  const params = new URLSearchParams(filters);
  return request<{ trades: Trade[]; total: number }>(`/api/trades/history?${params}`);
};
export const fetchEquitySnapshots = (symbol?: string, days?: number) => {
  const params = new URLSearchParams();
  if (symbol) params.set('symbol', symbol);
  if (days) params.set('days', String(days));
  return request<EquitySnapshot[]>(`/api/equity/snapshots?${params}`);
};

// Intelligence
export const fetchSentiment = (symbol: string) =>
  request<SentimentData>(`/api/graph/sentiment/${symbol}`);
export const fetchCrisisStatus = () => request<CrisisStatus>('/api/graph/crisis');
export const toggleCrisisMode = (active: boolean) =>
  request<void>('/api/graph/crisis', { method: 'PUT', body: JSON.stringify({ active }) });
export const fetchNews = () => request<NewsItem[]>('/api/graph/news');

// Backtest
export const runBacktest = (config: BacktestConfig) =>
  request<{ id: string }>('/api/backtest/run', { method: 'POST', body: JSON.stringify(config) });
export const fetchBacktestResults = (id: string) =>
  request<BacktestResults>(`/api/backtest/results/${id}`);

// Config
export const fetchConfig = () => request<AppConfig>('/api/config');
export const updateConfig = (config: Partial<AppConfig>) =>
  request<AppConfig>('/api/config', { method: 'PUT', body: JSON.stringify(config) });

// Env
export const fetchEnvVars = () => request<EnvVariable[]>('/api/env');
export const updateEnvVars = (vars: EnvVariable[]) =>
  request<{ requires_restart: boolean }>('/api/env', { method: 'PUT', body: JSON.stringify(vars) });

// Markets
export const fetchMarkets = () => request<MarketPair[]>('/api/markets');
