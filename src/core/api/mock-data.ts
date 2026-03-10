export const mockEquityData = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().split('T')[0],
  balance: 10000 + Math.sin(i * 0.3) * 500 + i * 30 + Math.random() * 200,
}));

export const mockTrades = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  timestamp: Date.now() - (49 - i) * 3600000 * 4,
  symbol: 'BTC/USDT',
  side: Math.random() > 0.5 ? 'long' as const : 'short' as const,
  action: Math.random() > 0.5 ? 'OPEN' as const : 'CLOSE' as const,
  price: 65000 + Math.random() * 5000,
  size: 0.01 + Math.random() * 0.05,
  notional: 650 + Math.random() * 250,
  fee: 0.5 + Math.random() * 2,
  pnl: Math.random() > 0.45 ? Math.random() * 200 : -Math.random() * 150,
  pnl_pct: (Math.random() - 0.45) * 5,
  reason: ['Signal', 'Stop Loss', 'Take Profit', 'Manual'][Math.floor(Math.random() * 4)],
  stop_loss: 64000 + Math.random() * 1000,
  take_profit: 69000 + Math.random() * 2000,
}));

export const mockNewsItems = [
  { id: '1', title: 'Bitcoin surges past $67K as institutional demand grows', source: 'CoinDesk', published_at: Date.now() - 180000, sentiment_score: 0.8, impact_level: 0.9, assets: ['BTC'], sectors: ['L1'] },
  { id: '2', title: 'SEC delays decision on spot ETH ETF applications', source: 'CryptoPanic', published_at: Date.now() - 720000, sentiment_score: -0.3, impact_level: 0.7, assets: ['ETH'], sectors: ['L1', 'DeFi'] },
  { id: '3', title: 'Solana DeFi TVL reaches new all-time high', source: 'The Block', published_at: Date.now() - 1800000, sentiment_score: 0.6, impact_level: 0.5, assets: ['SOL'], sectors: ['DeFi'] },
  { id: '4', title: 'Federal Reserve signals potential rate cuts in 2025', source: 'Reuters', published_at: Date.now() - 3600000, sentiment_score: 0.4, impact_level: 0.8, assets: ['BTC', 'ETH'], sectors: ['Macro'] },
  { id: '5', title: 'Major exchange reports record-breaking trading volume', source: 'CoinTelegraph', published_at: Date.now() - 5400000, sentiment_score: 0.5, impact_level: 0.4, assets: ['BTC'], sectors: ['Exchange'] },
  { id: '6', title: 'Whale alert: 5000 BTC moved to exchange wallets', source: 'Whale Alert', published_at: Date.now() - 7200000, sentiment_score: -0.4, impact_level: 0.6, assets: ['BTC'], sectors: ['On-chain'] },
  { id: '7', title: 'New stablecoin regulations proposed in EU parliament', source: 'CoinDesk', published_at: Date.now() - 10800000, sentiment_score: -0.2, impact_level: 0.5, assets: ['USDT', 'USDC'], sectors: ['Regulation'] },
  { id: '8', title: 'Layer 2 networks see 300% growth in daily transactions', source: 'The Block', published_at: Date.now() - 14400000, sentiment_score: 0.7, impact_level: 0.3, assets: ['ETH'], sectors: ['L2'] },
];

export const mockCircuitBreakers = [
  { name: 'Daily Loss', limit: -5, current: -1.91, status: 'ok' as const },
  { name: 'Consecutive Losses', limit: 3, current: 1, status: 'ok' as const },
  { name: 'Weekly Loss', limit: -10, current: -3.2, status: 'ok' as const },
  { name: 'Black Swan', limit: 10, current: 2.1, status: 'ok' as const },
  { name: 'Volatility Spike', limit: 5, current: 3.8, status: 'warn' as const },
];

export const mockBacktestResults = {
  total_pnl: 2847.32,
  total_return_pct: 28.47,
  sharpe_ratio: 1.42,
  sortino_ratio: 2.15,
  max_drawdown_pct: 8.3,
  profit_factor: 1.87,
  win_rate_pct: 58.2,
  avg_win_loss_ratio: 1.65,
  total_trades: 156,
  wins: 91,
  losses: 65,
  avg_trade_duration_hours: 4.2,
  best_trade_pnl: 412.50,
  worst_trade_pnl: -187.30,
};

export const mockMonthlyReturns = [
  { year: 2024, month: 1, return_pct: 5.2 },
  { year: 2024, month: 2, return_pct: -2.1 },
  { year: 2024, month: 3, return_pct: 8.4 },
  { year: 2024, month: 4, return_pct: -1.3 },
  { year: 2024, month: 5, return_pct: 3.7 },
  { year: 2024, month: 6, return_pct: -4.2 },
  { year: 2024, month: 7, return_pct: 6.1 },
  { year: 2024, month: 8, return_pct: 2.8 },
  { year: 2024, month: 9, return_pct: -0.9 },
  { year: 2024, month: 10, return_pct: 7.3 },
  { year: 2024, month: 11, return_pct: 4.5 },
  { year: 2024, month: 12, return_pct: -1.8 },
  { year: 2025, month: 1, return_pct: 3.2 },
  { year: 2025, month: 2, return_pct: 6.8 },
  { year: 2025, month: 3, return_pct: 2.1 },
];

export const mockWalkForwardWindows = [
  { train_start: '2024-01-01', train_end: '2024-06-30', test_start: '2024-07-01', test_end: '2024-09-30', in_sample_sharpe: 1.65, out_sample_sharpe: 1.42, degradation_pct: -13.9 },
  { train_start: '2024-04-01', train_end: '2024-09-30', test_start: '2024-10-01', test_end: '2024-12-31', in_sample_sharpe: 1.78, out_sample_sharpe: 1.51, degradation_pct: -15.2 },
  { train_start: '2024-07-01', train_end: '2024-12-31', test_start: '2025-01-01', test_end: '2025-03-09', in_sample_sharpe: 1.55, out_sample_sharpe: 1.38, degradation_pct: -11.0 },
];

export const mockBootstrapCIs = [
  { metric: 'Sharpe Ratio', point_estimate: 1.42, ci_lower: 1.18, ci_upper: 1.65, excludes_zero: true },
  { metric: 'Max Drawdown %', point_estimate: -8.3, ci_lower: -12.1, ci_upper: -5.2, excludes_zero: true },
  { metric: 'Profit Factor', point_estimate: 1.87, ci_lower: 1.52, ci_upper: 2.21, excludes_zero: true },
];
