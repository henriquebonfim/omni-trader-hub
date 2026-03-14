import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchStrategies, saveStrategy, updateStrategy, deleteStrategy, fetchStrategyPerformance } from '@/domains/strategy/api';

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: vi.fn(),
}));

vi.mock('@/core/api', () => ({ request: mockRequest }));

vi.mock('@/lib/adapters', () => ({
  adaptStrategy: vi.fn((strat) => ({ ...strat, adapted: true })),
}));

describe('strategy api', () => {
  beforeEach(() => {
    mockRequest.mockClear();
  });

  it('fetchStrategies calls GET /api/strategies and adapts', async () => {
    mockRequest.mockResolvedValueOnce({ strategies: [{ name: 'strat1' }], active: 'strat1' });
    const res = await fetchStrategies();
    expect(mockRequest).toHaveBeenCalledWith('/api/strategies');
    expect(res).toHaveLength(1);
    expect(res[0].name).toBe('strat1');
    expect((res[0] as any).adapted).toBe(true);
  });

  it('fetchStrategies returns [] on error', async () => {
    mockRequest.mockRejectedValueOnce(new Error('Network Error'));
    const res = await fetchStrategies();
    expect(res).toEqual([]);
  });

  it('fetchStrategyPerformance maps performance correctly', async () => {
    mockRequest.mockResolvedValueOnce({
      performance: {
        trending: [{ name: 'strat1', sample_size: 10, sharpe: 1.5, profit_factor: 2.0, win_rate: 0.6, composite_score: 80 }]
      }
    });
    const res = await fetchStrategyPerformance();
    expect(mockRequest).toHaveBeenCalledWith('/api/strategies/performance');
    expect(res).toHaveLength(1);
    expect(res[0].name).toBe('strat1');
    expect(res[0].regime).toBe('trending');
    expect(res[0].sharpe).toBe(1.5);
  });

  it('saveStrategy calls POST /api/strategies', async () => {
    mockRequest.mockResolvedValueOnce({ name: 'new-strat' });
    const strat = { name: 'new-strat' };
    const res = await saveStrategy(strat as any);
    expect(mockRequest).toHaveBeenCalledWith('/api/strategies', {
      method: 'POST',
      body: JSON.stringify(strat),
    });
    expect(res.name).toBe('new-strat');
  });

  it('updateStrategy calls PUT /api/strategies/:name', async () => {
    mockRequest.mockResolvedValueOnce({ name: 'strat1' });
    const strat = { name: 'strat1', code: 'updated' };
    const res = await updateStrategy('strat1', strat as any);
    expect(mockRequest).toHaveBeenCalledWith('/api/strategies/strat1', {
      method: 'PUT',
      body: JSON.stringify(strat),
    });
    expect(res.name).toBe('strat1');
  });

  it('deleteStrategy calls DELETE /api/strategies/:name', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await deleteStrategy('strat1');
    expect(mockRequest).toHaveBeenCalledWith('/api/strategies/strat1', {
      method: 'DELETE',
    });
  });
});
