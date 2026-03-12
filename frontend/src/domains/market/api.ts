import { request } from '@/core/api';
import type { CrisisStatus } from '@/domains/system/types';
import { stubMarkets } from '@/lib/stubs';
import type { CorrelationMatrixData, MarketPair, NewsItem, SentimentData } from './types';

export const fetchSentiment = async (symbol: string) => {
  return request<SentimentData>(`/api/graph/sentiment/${encodeURIComponent(symbol)}`);
};

export const fetchCrisisStatus = async () => {
  return request<CrisisStatus>('/api/graph/crisis');
};

export const toggleCrisisMode = (active: boolean) =>
  request<void>('/api/graph/crisis', { method: 'PUT', body: JSON.stringify({ active }) });

export const fetchNews = async () => {
  return request<NewsItem[]>('/api/graph/news');
};

export const fetchMarkets = async () => {
  try {
    return await request<MarketPair[]>('/api/markets');
  } catch (e) {
    console.warn('fetchMarkets stubbed', e);
    return stubMarkets();
  }
};

export const fetchCorrelationMatrix = async (
  params?: { timeframe?: string; limit?: number; symbols?: string[] },
) => {
  const search = new URLSearchParams();
  if (params?.timeframe) search.set('timeframe', params.timeframe);
  if (params?.limit) search.set('limit', String(params.limit));
  if (params?.symbols?.length) search.set('symbols', params.symbols.join(','));

  const query = search.toString();
  const path = query ? `/api/graph/correlation-matrix?${query}` : '/api/graph/correlation-matrix';
  return request<CorrelationMatrixData>(path);
};
