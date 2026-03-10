import type { EnvVariable, AlertMessage } from './types';

export const mockEnvVars: EnvVariable[] = [
  { key: 'BINANCE_API_KEY', value: 'abc123...xyz', masked: true, category: 'Binance API', description: 'Binance Futures API key', requires_restart: true },
  { key: 'BINANCE_SECRET', value: 'secret...key', masked: true, category: 'Binance API', description: 'Binance API secret', requires_restart: true },
  { key: 'MEMGRAPH_HOST', value: 'memgraph', masked: false, category: 'Database', description: 'Memgraph hostname', requires_restart: true },
  { key: 'MEMGRAPH_PORT', value: '7687', masked: false, category: 'Database', description: 'Bolt protocol port', requires_restart: true },
  { key: 'REDIS_HOST', value: 'redis', masked: false, category: 'Redis', description: 'Redis hostname', requires_restart: true },
  { key: 'REDIS_PORT', value: '6379', masked: false, category: 'Redis', description: 'Redis port', requires_restart: true },
  { key: 'DISCORD_WEBHOOK_URL', value: 'https://discord.com/api/webhooks/...', masked: true, category: 'Notifications', description: 'Discord webhook for alerts', requires_restart: false },
  { key: 'OMNITRADER_API_KEY', value: 'omni_key_...', masked: true, category: 'Security', description: 'API auth key', requires_restart: true },
];

export const mockAlerts: AlertMessage[] = [
  { type: 'alert', level: 'info', title: 'Strategy Rotation', body: 'BTC/USDT switched from EMA Volume to ADX Trend (regime: TRENDING)', timestamp: Date.now() - 120000 },
  { type: 'alert', level: 'warning', title: 'Circuit Breaker Warning', body: 'SOL/USDT daily loss at -3.8% (limit: -5%)', timestamp: Date.now() - 300000 },
  { type: 'alert', level: 'critical', title: 'High Volatility Detected', body: 'BTC 1h move: 4.2% — approaching black swan threshold', timestamp: Date.now() - 600000 },
  { type: 'alert', level: 'info', title: 'Trade Executed', body: 'ETH/USDT LONG opened at $3,542.18', timestamp: Date.now() - 900000 },
  { type: 'alert', level: 'info', title: 'Bot Started', body: 'DOGE/USDT bot started in auto mode', timestamp: Date.now() - 1800000 },
];
