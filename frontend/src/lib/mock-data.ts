import type { Bot, Trade, Strategy, AlertMessage, NewsItem, EquitySnapshot, CircuitBreaker, BacktestResults, MarketPair, EnvVariable } from '@/types';

// ===== Mock Bots =====
export const mockBots: Bot[] = [
  {
    id: 'bot-1', symbol: 'BTC/USDT', status: 'running', mode: 'auto',
    active_strategy: 'ADX Trend', regime: 'trending',
    position: { side: 'long', entry_price: 67250, size: 0.15, unrealized_pnl: 312.50, stop_loss: 65800, take_profit: 70000, opened_at: Date.now() - 3600000 },
    daily_pnl: 485.20, daily_pnl_pct: 2.42, balance_allocated: 20000, leverage: 3, created_at: Date.now() - 86400000 * 7,
  },
  {
    id: 'bot-2', symbol: 'ETH/USDT', status: 'running', mode: 'auto',
    active_strategy: 'Bollinger Bands', regime: 'ranging',
    position: null,
    daily_pnl: 123.80, daily_pnl_pct: 0.83, balance_allocated: 15000, leverage: 3, created_at: Date.now() - 86400000 * 5,
  },
  {
    id: 'bot-3', symbol: 'SOL/USDT', status: 'running', mode: 'manual',
    active_strategy: 'Breakout', regime: 'volatile',
    position: { side: 'short', entry_price: 178.50, size: 100, unrealized_pnl: -45.00, stop_loss: 185.00, take_profit: 165.00, opened_at: Date.now() - 1800000 },
    daily_pnl: -89.30, daily_pnl_pct: -0.89, balance_allocated: 10000, leverage: 5, created_at: Date.now() - 86400000 * 3,
  },
  {
    id: 'bot-4', symbol: 'DOGE/USDT', status: 'paused', mode: 'auto',
    active_strategy: 'EMA Volume', regime: 'trending',
    position: null,
    daily_pnl: 0, daily_pnl_pct: 0, balance_allocated: 5000, leverage: 2, created_at: Date.now() - 86400000 * 10,
  },
  {
    id: 'bot-5', symbol: 'AVAX/USDT', status: 'stopped', mode: 'auto',
    active_strategy: '', regime: 'ranging',
    position: null,
    daily_pnl: 0, daily_pnl_pct: 0, balance_allocated: 8000, leverage: 3, created_at: Date.now() - 86400000 * 14,
  },
];

export const mockPrices: Record<string, number> = {
  'BTC/USDT': 67562.40,
  'ETH/USDT': 3542.18,
  'SOL/USDT': 176.92,
  'DOGE/USDT': 0.1842,
  'AVAX/USDT': 38.65,
};

// ===== Mock Trades =====
export const mockTrades: Trade[] = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  timestamp: Date.now() - i * 3600000 * 2,
  bot_id: mockBots[i % 3].id,
  symbol: mockBots[i % 3].symbol,
  side: i % 2 === 0 ? 'long' as const : 'short' as const,
  action: i % 4 === 0 ? 'OPEN' as const : 'CLOSE' as const,
  strategy: ['ADX Trend', 'Bollinger Bands', 'Breakout', 'EMA Volume'][i % 4],
  price: 67000 + Math.random() * 1000,
  size: 0.1 + Math.random() * 0.2,
  notional: 6700 + Math.random() * 200,
  fee: 2.5 + Math.random() * 1.5,
  pnl: i % 4 !== 0 ? (Math.random() - 0.4) * 200 : undefined,
  pnl_pct: i % 4 !== 0 ? (Math.random() - 0.4) * 3 : undefined,
  reason: ['Signal: LONG', 'Signal: EXIT_LONG', 'Stop Loss Hit', 'Take Profit Hit'][i % 4],
}));

// ===== Mock Strategies =====
export const mockStrategies: Strategy[] = [
  { name: 'ADX Trend', description: 'Trend-following using ADX(14) + EMA crossover. Best in TRENDING regime.', regime_affinity: 'trending', builtin: true, win_rate: 52, sharpe: 1.8, avg_trade: 1.2, active_bots: 2 },
  { name: 'Bollinger Bands', description: 'Mean-reversion with BB(20,2σ) + RSI(14). Best in RANGING regime.', regime_affinity: 'ranging', builtin: true, win_rate: 58, sharpe: 1.4, avg_trade: 0.8, active_bots: 1 },
  { name: 'Breakout', description: 'Donchian channel breakout (20-period). Best post-consolidation.', regime_affinity: 'volatile', builtin: true, win_rate: 45, sharpe: 1.6, avg_trade: 1.5, active_bots: 1 },
  { name: 'EMA Volume', description: 'EMA(9)/EMA(21) crossover confirmed by volume spike. Best in TRENDING.', regime_affinity: 'trending', builtin: true, win_rate: 50, sharpe: 1.3, avg_trade: 0.9, active_bots: 1 },
  { name: 'Z-Score', description: 'Statistical mean-reversion using z-score(20). Best in RANGING.', regime_affinity: 'ranging', builtin: true, win_rate: 55, sharpe: 1.5, avg_trade: 0.7, active_bots: 0 },
];

// ===== Mock Alerts =====
export const mockAlerts: AlertMessage[] = [
  { type: 'alert', level: 'info', title: 'Strategy Rotation', body: 'BTC/USDT switched from EMA Volume to ADX Trend (regime: TRENDING)', timestamp: Date.now() - 120000 },
  { type: 'alert', level: 'warning', title: 'Circuit Breaker Warning', body: 'SOL/USDT daily loss at -3.8% (limit: -5%)', timestamp: Date.now() - 300000 },
  { type: 'alert', level: 'critical', title: 'High Volatility Detected', body: 'BTC 1h move: 4.2% — approaching black swan threshold', timestamp: Date.now() - 600000 },
  { type: 'alert', level: 'info', title: 'Trade Executed', body: 'ETH/USDT LONG opened at $3,542.18', timestamp: Date.now() - 900000 },
  { type: 'alert', level: 'info', title: 'Bot Started', body: 'DOGE/USDT bot started in auto mode', timestamp: Date.now() - 1800000 },
];

// ===== Mock News =====
export const mockNews: NewsItem[] = [
  { id: '1', title: 'Bitcoin ETF Sees Record Inflows of $1.2B', source: 'CoinDesk', published_at: Date.now() - 1800000, sentiment_score: 0.8, impact_level: 0.9, assets: ['BTC'], sectors: ['ETF'] },
  { id: '2', title: 'Ethereum Dencun Upgrade Shows 90% Fee Reduction', source: 'The Block', published_at: Date.now() - 3600000, sentiment_score: 0.6, impact_level: 0.7, assets: ['ETH'], sectors: ['L2'] },
  { id: '3', title: 'SEC Delays Decision on Solana ETF Application', source: 'Bloomberg', published_at: Date.now() - 7200000, sentiment_score: -0.3, impact_level: 0.8, assets: ['SOL'], sectors: ['Regulation'] },
  { id: '4', title: 'Federal Reserve Signals Potential Rate Cut in Q3', source: 'Reuters', published_at: Date.now() - 10800000, sentiment_score: 0.5, impact_level: 0.6, assets: ['BTC', 'ETH'], sectors: ['Macro'] },
  { id: '5', title: 'Dogecoin Whale Moves 500M DOGE to Unknown Wallet', source: 'Whale Alert', published_at: Date.now() - 14400000, sentiment_score: -0.2, impact_level: 0.4, assets: ['DOGE'], sectors: ['On-chain'] },
];

// ===== Mock Equity =====
export const mockEquitySnapshots: EquitySnapshot[] = Array.from({ length: 90 }, (_, i) => ({
  timestamp: Date.now() - (89 - i) * 86400000,
  equity: 50000 + i * 120 + Math.sin(i * 0.3) * 800 + Math.random() * 300,
}));

// ===== Mock Circuit Breakers =====
export const mockCircuitBreakers: CircuitBreaker[] = [
  { name: 'Daily Loss', limit: '-5%', current: '-1.2%', current_pct: 24, status: 'ok' },
  { name: 'Consecutive Losses', limit: '3 max', current: '1', current_pct: 33, status: 'ok' },
  { name: 'Weekly Loss', limit: '-10%', current: '-3.5%', current_pct: 35, status: 'ok' },
  { name: 'Black Swan', limit: '>10% move', current: '2.1%', current_pct: 21, status: 'ok' },
  { name: 'Volatility Spike', limit: '>3× ATR', current: '1.8×', current_pct: 60, status: 'warning' },
];

// ===== Mock Backtest Results =====
export const mockBacktestResults: BacktestResults = {
  id: 'bt-1',
  config: { symbol: 'BTC/USDT', start_date: '2024-01-01', end_date: '2024-06-30', strategy: 'ADX Trend', timeframe: '1h', initial_capital: 10000, position_size_pct: 5, leverage: 3 },
  total_pnl: 3245.80, total_return_pct: 32.46, sharpe_ratio: 1.82, sortino_ratio: 2.15,
  max_drawdown_pct: 8.3, profit_factor: 1.85, win_rate_pct: 54.2, avg_win_loss_ratio: 1.68,
  total_trades: 142, wins: 77, losses: 65, avg_trade_duration_hours: 4.2,
  best_trade_pnl: 892.50, worst_trade_pnl: -312.40,
  equity_curve: Array.from({ length: 180 }, (_, i) => ({
    timestamp: new Date('2024-01-01').getTime() + i * 86400000,
    equity: 10000 + i * 18 + Math.sin(i * 0.15) * 400 + Math.random() * 100,
    drawdown: Math.max(0, Math.sin(i * 0.1) * 5 + Math.random() * 2),
  })),
  monthly_returns: [
    { year: 2024, month: 1, return_pct: 5.2 }, { year: 2024, month: 2, return_pct: 8.1 },
    { year: 2024, month: 3, return_pct: -2.3 }, { year: 2024, month: 4, return_pct: 6.8 },
    { year: 2024, month: 5, return_pct: 11.4 }, { year: 2024, month: 6, return_pct: 3.2 },
  ],
  trades: mockTrades.slice(0, 20),
};

// ===== Mock Markets =====
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

// ===== Mock Env Variables =====
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
