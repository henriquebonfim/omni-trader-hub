import { request } from '@/core/api';
import type { SentimentData, NewsItem, MarketPair } from './types';
import type { CrisisStatus } from '@/domains/system/types';
import { stubSentiment, stubCrisis, stubNews, stubMarkets } from '@/lib/stubs';

export const fetchSentiment = async (symbol: string) => {
  try {
    return await request<SentimentData>(`/api/graph/sentiment/${symbol}`);
  } catch (e) {
    console.warn('fetchSentiment stubbed', e);
    return stubSentiment();
  }
};
export const fetchCrisisStatus = async () => {
  try {
    return await request<CrisisStatus>('/api/graph/crisis');
  } catch (e) {
    console.warn('fetchCrisisStatus stubbed', e);
    return stubCrisis();
  }
};
export const toggleCrisisMode = (active: boolean) =>
  request<void>('/api/graph/crisis', { method: 'PUT', body: JSON.stringify({ active }) });
export const fetchNews = async () => {
  try {
    return await request<NewsItem[]>('/api/graph/news');
  } catch (e) {
    console.warn('fetchNews stubbed', e);
    return stubNews();
  }
};
export const fetchMarkets = async () => {
  try {
    return await request<MarketPair[]>('/api/markets');
  } catch (e) {
    console.warn('fetchMarkets stubbed', e);
    return stubMarkets();
  }
};
