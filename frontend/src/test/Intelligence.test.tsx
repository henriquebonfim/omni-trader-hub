import { describe, it, expect, mock, beforeEach } from 'bun:test';

const mockRequest = mock(() => Promise.resolve({}));

mock.module('@/core/api', () => ({ request: mockRequest }));
mock.module('@/lib/stubs', () => ({ stubMarkets: mock(() => []) }));

// Import after mocking
const { fetchSentiment, fetchCrisisStatus, fetchNews, fetchMarkets } = await import(
  '@/domains/market/api'
);

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

  it('fetchMarkets falls back to stub on error', async () => {
    mockRequest.mockRejectedValueOnce(new Error('network error'));
    const result = await fetchMarkets();
    expect(Array.isArray(result)).toBe(true);
  });
});
