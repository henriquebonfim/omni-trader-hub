import { request } from '@/core/api';
import type { SentimentData, NewsItem, MarketPair } from './types';
import type { CrisisStatus } from '@/domains/system/types';

export const fetchSentiment = (symbol: string) =>
  request<SentimentData>(`/api/graph/sentiment/${symbol}`);
export const fetchCrisisStatus = () => request<CrisisStatus>('/api/graph/crisis');
export const toggleCrisisMode = (active: boolean) =>
  request<void>('/api/graph/crisis', { method: 'PUT', body: JSON.stringify({ active }) });
export const fetchNews = () => request<NewsItem[]>('/api/graph/news');
export const fetchMarkets = () => request<MarketPair[]>('/api/markets');
