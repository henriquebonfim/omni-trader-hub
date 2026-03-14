import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchBots, createBot, updateBot, deleteBot, startBot, stopBot } from '@/domains/bot/api';

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: vi.fn(),
}));

vi.mock('@/core/api', () => ({ request: mockRequest }));

// Simple adapter mock
vi.mock('@/lib/adapters', () => ({
  adaptBot: vi.fn((bot) => ({ ...bot, id: bot.id || 'default' })),
}));

describe('bot api', () => {
  beforeEach(() => {
    mockRequest.mockClear();
  });

  it('fetchBots should call /api/bots and adapt results', async () => {
    mockRequest.mockResolvedValueOnce([{ id: 'bot-1', symbol: 'BTC/USDT' }]);

    const bots = await fetchBots();
    
    expect(mockRequest).toHaveBeenCalledTimes(1);
    expect(mockRequest).toHaveBeenCalledWith('/api/bots');
    expect(bots).toHaveLength(1);
    expect(bots[0].id).toBe('bot-1');
  });

  it('fetchBots should return empty array on error', async () => {
    mockRequest.mockRejectedValueOnce(new Error('Network Error'));
    
    const bots = await fetchBots();
    
    expect(mockRequest).toHaveBeenCalledTimes(1);
    expect(bots).toEqual([]);
  });

  it('createBot calls POST /api/bots', async () => {
    mockRequest.mockResolvedValueOnce({ ok: true, bot_id: 'new-bot' });
    const config = { name: 'Bot 1' };
    const res = await createBot(config);
    expect(mockRequest).toHaveBeenCalledWith('/api/bots', {
      method: 'POST',
      body: JSON.stringify({ config }),
    });
    expect(res.bot_id).toBe('new-bot');
  });

  it('updateBot calls PUT /api/bots/:id', async () => {
    mockRequest.mockResolvedValueOnce({ id: 'bot-1' });
    const config = { name: 'Bot 2' };
    const res = await updateBot('bot-1', config);
    expect(mockRequest).toHaveBeenCalledWith('/api/bots/bot-1', {
      method: 'PUT',
      body: JSON.stringify({ config }),
    });
    expect(res.id).toBe('bot-1');
  });

  it('deleteBot calls DELETE /api/bots/:id', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await deleteBot('bot-1');
    expect(mockRequest).toHaveBeenCalledWith('/api/bots/bot-1', {
      method: 'DELETE',
    });
  });

  it('startBot calls POST /api/bot/start for default bot', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await startBot('default');
    expect(mockRequest).toHaveBeenCalledWith('/api/bot/start', {
      method: 'POST',
    });
  });

  it('startBot calls POST /api/bots/:id/start for other bots', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await startBot('bot-1');
    expect(mockRequest).toHaveBeenCalledWith('/api/bots/bot-1/start', {
      method: 'POST',
    });
  });

  it('stopBot calls POST /api/bot/stop?confirm=true for default bot', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await stopBot('default');
    expect(mockRequest).toHaveBeenCalledWith('/api/bot/stop?confirm=true', {
      method: 'POST',
    });
  });

  it('stopBot calls POST /api/bots/:id/stop?confirm=true for other bots', async () => {
    mockRequest.mockResolvedValueOnce(undefined);
    await stopBot('bot-1');
    expect(mockRequest).toHaveBeenCalledWith('/api/bots/bot-1/stop?confirm=true', {
      method: 'POST',
    });
  });
});
