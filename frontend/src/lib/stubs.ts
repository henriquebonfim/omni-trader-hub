import type { Bot } from '@/domains/bot/types';
import type { SentimentData, NewsItem, MarketPair } from '@/domains/market/types';
import type { CrisisStatus, EnvVariable } from '@/domains/system/types';
import type { BacktestResults } from '@/domains/trade/types';
import { mockBots } from '@/domains/bot/mocks';
import { mockBacktestResults } from '@/domains/trade/mocks';

// STUB: replaced by T37
export function stubBots(realBot?: Bot): Bot[] {
  if (realBot) {
    return [realBot, ...mockBots.slice(1)];
  }
  return mockBots;
}

// STUB: replaced by T33/T34
export function stubSentiment(): SentimentData {
  return {
    score: 0,
    label: 'Neutral',
    article_count: 0,
    max_impact: 0,
  };
}

// STUB: replaced by T34
export function stubCrisis(): CrisisStatus {
  return {
    active: false,
    source: 'auto',
  };
}

// STUB: replaced by T33
export function stubNews(): NewsItem[] {
  return [];
}

// STUB: replaced by T35
export function stubBacktestResults(): BacktestResults {
  return mockBacktestResults;
}

// STUB: replaced by T42
export function stubMarkets(): MarketPair[] {
  return [
    { symbol: 'BTC/USDT', base: 'BTC', quote: 'USDT', volume_24h: 1250000000, last_price: 67500.0 },
    { symbol: 'ETH/USDT', base: 'ETH', quote: 'USDT', volume_24h: 890000000, last_price: 3245.5 },
    { symbol: 'SOL/USDT', base: 'SOL', quote: 'USDT', volume_24h: 450000000, last_price: 145.2 },
    { symbol: 'BNB/USDT', base: 'BNB', quote: 'USDT', volume_24h: 210000000, last_price: 590.1 },
    { symbol: 'XRP/USDT', base: 'XRP', quote: 'USDT', volume_24h: 180000000, last_price: 0.62 },
  ];
}

// STUB: replaced by T41
export function stubEnvVars(): EnvVariable[] {
  return [
    { key: 'BINANCE_API_KEY', value: '••••••••••••••••', masked: true, category: 'Binance API Credentials', description: 'Binance Futures API key', requires_restart: true },
    { key: 'BINANCE_SECRET', value: '••••••••••••••••', masked: true, category: 'Binance API Credentials', description: 'Binance API secret', requires_restart: true },
    { key: 'MEMGRAPH_HOST', value: 'memgraph', masked: false, category: 'Database (Memgraph)', description: 'Memgraph hostname', requires_restart: true },
    { key: 'MEMGRAPH_PORT', value: '7687', masked: false, category: 'Database (Memgraph)', description: 'Bolt protocol port', requires_restart: true },
    { key: 'REDIS_HOST', value: 'redis', masked: false, category: 'Redis', description: 'Redis hostname', requires_restart: true },
    { key: 'DISCORD_WEBHOOK_URL', value: 'https://discord.com/api/webhooks/...', masked: true, category: 'Notifications', description: 'Discord webhook for alerts', requires_restart: false },
    { key: 'OMNITRADER_API_KEY', value: '••••••••••••••••', masked: true, category: 'Security', description: 'API auth key', requires_restart: false },
  ];
}
