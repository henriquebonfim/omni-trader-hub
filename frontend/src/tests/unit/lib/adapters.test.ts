import { describe, expect, it } from 'vitest';
import { adaptBot, adaptTrade, adaptStrategy } from '@/lib/adapters';

describe('adapters unit tests', () => {
  it('adaptBot should handle empty or missing fields', () => {
    const raw = { id: 'bot-1' };
    const bot = adaptBot(raw as any);
    
    expect(bot.id).toBe('bot-1');
    expect(bot.symbol).toBe('BTC/USDT'); // default
    expect(bot.status).toBe('stopped');
    expect(bot.daily_pnl).toBe(0);
    expect(bot.position).toBeNull();
  });

  it('adaptBot should correctly map nested position', () => {
    const raw = {
      id: 'bot-1',
      running: true,
      position: {
        is_open: true,
        side: 'short',
        entry_price: 50000,
        size: 0.1,
        timestamp: '2024-03-20T10:00:00Z'
      }
    };
    const bot = adaptBot(raw as any);
    
    expect(bot.status).toBe('running');
    expect(bot.position?.side).toBe('short');
    expect(bot.position?.entry_price).toBe(50000);
    expect(bot.position?.opened_at).toBe(new Date('2024-03-20T10:00:00Z').getTime());
  });

  it('adaptTrade should handle string and numeric IDs', () => {
    const trade1 = adaptTrade({ id: '123' } as any);
    const trade2 = adaptTrade({ id: 456 } as any);
    
    expect(trade1.id).toBe(123);
    expect(trade2.id).toBe(456);
  });

  it('adaptStrategy should normalize regime_affinity', () => {
    const s1 = adaptStrategy({ name: 'S1', regime_affinity: 'trending' } as any);
    const s2 = adaptStrategy({ name: 'S2', regime_affinity: ['volatile'] } as any);
    const s3 = adaptStrategy({ name: 'S3', regime_affinity: 'invalid' } as any);
    
    expect(s1.regime_affinity).toBe('trending');
    expect(s2.regime_affinity).toBe('volatile');
    expect(s3.regime_affinity).toBe('all');
  });
});
