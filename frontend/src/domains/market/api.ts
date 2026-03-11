import { request } from '@/core/api';
import type { SentimentData, NewsItem, MarketPair } from './types';
import type { CrisisStatus } from '@/domains/system/types';
import { stubMarkets } from '@/lib/stubs';

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
