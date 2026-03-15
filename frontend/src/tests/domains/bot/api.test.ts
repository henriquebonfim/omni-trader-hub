import { describe, expect, it } from 'vitest';
import { fetchBots, createBot, updateBot, deleteBot, startBot, stopBot } from '@/domains/bot/api';
import { server } from '@/tests/mocks/server';
import { http, HttpResponse } from 'msw';

const API_BASE = 'http://localhost:8000';

describe('bot api (MSW)', () => {
  it('fetchBots should return bots from server', async () => {
    const bots = await fetchBots();
    
    expect(bots).toHaveLength(2);
    expect(bots[0].id).toBe('bot-1');
    expect(bots[1].id).toBe('bot-2');
  });

  it('fetchBots should return empty array on server error', async () => {
    // Override handler for this test
    server.use(
      http.get(`${API_BASE}/api/bots`, () => {
        return new HttpResponse(null, { status: 500 });
      })
    );
    
    const bots = await fetchBots();
    expect(bots).toEqual([]);
  });

  it('createBot sends correct data and returns result', async () => {
    const config = { name: 'New Bot' };
    const res = await createBot(config);
    
    expect(res.ok).toBe(true);
    expect(res.bot_id).toBe('new-bot');
  });

  it('updateBot calls correct endpoint', async () => {
    let capturedId = '';
    server.use(
      http.put(`${API_BASE}/api/bots/:id`, ({ params }) => {
        capturedId = params.id as string;
        return HttpResponse.json({ id: capturedId });
      })
    );

    const res = await updateBot('bot-abc', { name: 'Updated' });
    expect(capturedId).toBe('bot-abc');
    expect(res.id).toBe('bot-abc');
  });

  it('deleteBot calls correct endpoint', async () => {
    let called = false;
    server.use(
      http.delete(`${API_BASE}/api/bots/:id`, () => {
        called = true;
        return new HttpResponse(null, { status: 204 });
      })
    );

    await deleteBot('bot-123');
    expect(called).toBe(true);
  });

  it('startBot handles default and specific bot IDs', async () => {
    let lastUrl = '';
    server.use(
      http.post(`${API_BASE}/api/bot/start`, ({ request }) => {
        lastUrl = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 200 });
      }),
      http.post(`${API_BASE}/api/bots/:id/start`, ({ request }) => {
        lastUrl = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 200 });
      })
    );

    await startBot('default');
    expect(lastUrl).toBe('/api/bot/start');

    await startBot('bot-99');
    expect(lastUrl).toBe('/api/bots/bot-99/start');
  });

  it('stopBot handles default and specific bot IDs', async () => {
    let lastUrl = '';
    server.use(
      http.post(`${API_BASE}/api/bot/stop`, ({ request }) => {
        lastUrl = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 200 });
      }),
      http.post(`${API_BASE}/api/bots/:id/stop`, ({ request }) => {
        lastUrl = new URL(request.url).pathname;
        return new HttpResponse(null, { status: 200 });
      })
    );

    await stopBot('default');
    expect(lastUrl).toBe('/api/bot/stop');

    await stopBot('bot-88');
    expect(lastUrl).toBe('/api/bots/bot-88/stop');
  });
});
