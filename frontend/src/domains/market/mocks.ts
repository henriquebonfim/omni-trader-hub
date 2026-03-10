import type { NewsItem, MarketPair } from './types';

export const mockPrices: Record<string, number> = {
  'BTC/USDT': 67562.40,
  'ETH/USDT': 3542.18,
  'SOL/USDT': 176.92,
  'DOGE/USDT': 0.1842,
  'AVAX/USDT': 38.65,
};

export const mockNews: NewsItem[] = [
  { id: '1', title: 'Bitcoin ETF Sees Record Inflows of $1.2B', source: 'CoinDesk', published_at: Date.now() - 1800000, sentiment_score: 0.8, impact_level: 0.9, assets: ['BTC'], sectors: ['ETF'] },
  { id: '2', title: 'Ethereum Dencun Upgrade Shows 90% Fee Reduction', source: 'The Block', published_at: Date.now() - 3600000, sentiment_score: 0.6, impact_level: 0.7, assets: ['ETH'], sectors: ['L2'] },
  { id: '3', title: 'SEC Delays Decision on Solana ETF Application', source: 'Bloomberg', published_at: Date.now() - 7200000, sentiment_score: -0.3, impact_level: 0.8, assets: ['SOL'], sectors: ['Regulation'] },
  { id: '4', title: 'Federal Reserve Signals Potential Rate Cut in Q3', source: 'Reuters', published_at: Date.now() - 10800000, sentiment_score: 0.5, impact_level: 0.6, assets: ['BTC', 'ETH'], sectors: ['Macro'] },
  { id: '5', title: 'Dogecoin Whale Moves 500M DOGE to Unknown Wallet', source: 'Whale Alert', published_at: Date.now() - 14400000, sentiment_score: -0.2, impact_level: 0.4, assets: ['DOGE'], sectors: ['On-chain'] },
];

export const mockMarkets: MarketPair[] = [
  { symbol: 'BTC/USDT', base: 'BTC', quote: 'USDT', volume_24h: 28500000000, last_price: 67562.40 },
  { symbol: 'ETH/USDT', base: 'ETH', quote: 'USDT', volume_24h: 12800000000, last_price: 3542.18 },
  { symbol: 'SOL/USDT', base: 'SOL', quote: 'USDT', volume_24h: 4200000000, last_price: 176.92 },
  { symbol: 'DOGE/USDT', base: 'DOGE', quote: 'USDT', volume_24h: 1800000000, last_price: 0.1842 },
  { symbol: 'AVAX/USDT', base: 'AVAX', quote: 'USDT', volume_24h: 980000000, last_price: 38.65 },
  { symbol: 'ADA/USDT', base: 'ADA', quote: 'USDT', volume_24h: 750000000, last_price: 0.4521 },
  { symbol: 'DOT/USDT', base: 'DOT', quote: 'USDT', volume_24h: 520000000, last_price: 7.82 },
  { symbol: 'LINK/USDT', base: 'LINK', quote: 'USDT', volume_24h: 480000000, last_price: 14.35 },
  { symbol: 'MATIC/USDT', base: 'MATIC', quote: 'USDT', volume_24h: 340000000, last_price: 0.7123 },
  { symbol: 'XRP/USDT', base: 'XRP', quote: 'USDT', volume_24h: 2100000000, last_price: 0.5234 },
];
