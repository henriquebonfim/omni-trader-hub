import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: vi.fn(() => Promise.resolve({})),
}));

vi.mock('@/core/api', () => ({ request: mockRequest }));
vi.mock('@/lib/stubs', () => ({ stubMarkets: vi.fn(() => []) }));

import {
    fetchCorrelationMatrix,
    fetchCrisisStatus,
    fetchMarkets,
    fetchNews,
    fetchSentiment,
} from '@/domains/market/api';

describe('market api (real endpoints, no stubs)', () => {
  beforeEach(() => {
    mockRequest.mockClear();
  });

  it('fetchSentiment calls the correct endpoint with encoded symbol', async () => {
    mockRequest.mockResolvedValueOnce({ score: 0.5, label: 'Neutral', article_count: 10 });
    await fetchSentiment('BTC/USDT');
    expect(mockRequest).toHaveBeenCalledWith('/api/graph/sentiment/BTC%2FUSDT');
  });

  it('fetchCrisisStatus calls /api/graph/crisis', async () => {
    mockRequest.mockResolvedValueOnce({ active: false });
    await fetchCrisisStatus();
    expect(mockRequest).toHaveBeenCalledWith('/api/graph/crisis');
  });

  it('fetchNews calls /api/graph/news', async () => {
    mockRequest.mockResolvedValueOnce([]);
    await fetchNews();
    expect(mockRequest).toHaveBeenCalledWith('/api/graph/news');
  });

  it('fetchSentiment propagates errors (no stub fallback)', async () => {
    mockRequest.mockRejectedValueOnce(new Error('network error'));
    await expect(fetchSentiment('BTC/USDT')).rejects.toThrow('network error');
  });

  it('fetchCrisisStatus propagates errors (no stub fallback)', async () => {
    mockRequest.mockRejectedValueOnce(new Error('network error'));
    await expect(fetchCrisisStatus()).rejects.toThrow('network error');
  });

  it('fetchNews propagates errors (no stub fallback)', async () => {
    mockRequest.mockRejectedValueOnce(new Error('network error'));
    await expect(fetchNews()).rejects.toThrow('network error');
  });

  it('fetchCorrelationMatrix calls /api/graph/correlation-matrix with query params', async () => {
    mockRequest.mockResolvedValueOnce({ symbols: [], matrix: [] });
    await fetchCorrelationMatrix({ timeframe: '4h', limit: 240, symbols: ['BTC/USDT', 'ETH/USDT'] });
    expect(mockRequest).toHaveBeenCalledWith(
      '/api/graph/correlation-matrix?timeframe=4h&limit=240&symbols=BTC%2FUSDT%2CETH%2FUSDT'
    );
  });

  it('fetchMarkets falls back to stub on error', async () => {
    mockRequest.mockRejectedValueOnce(new Error('network error'));
    const result = await fetchMarkets();
    expect(Array.isArray(result)).toBe(true);
  });
});
