import { http, HttpResponse } from "msw";

const API_BASE = "http://localhost:8000";

export const handlers = [
  http.get(`${API_BASE}/api/bots`, () => {
    return HttpResponse.json([
      { id: "bot-1", symbol: "BTC/USDT", running: true, mode: "auto", strategy: "ema_volume" },
      { id: "bot-2", symbol: "ETH/USDT", running: false, mode: "manual", strategy: "scalper" },
    ]);
  }),
  
  http.post(`${API_BASE}/api/bots`, async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({ ok: true, bot_id: "new-bot", config: body.config }, { status: 201 });
  }),

  http.get(`${API_BASE}/api/strategies`, () => {
    return HttpResponse.json({
      strategies: [
        { name: "ema_volume", description: "EMA Cross with Volume", type: "builtin", regime_affinity: "trending" },
        { name: "scalper", description: "High frequency scalping", type: "builtin", regime_affinity: "volatile" },
      ]
    });
  }),

  http.get(`${API_BASE}/api/trades`, () => {
    return HttpResponse.json({
      trades: [],
      total: 0,
      pages: 1
    });
  }),

  http.get(`${API_BASE}/api/equity`, () => {
    return HttpResponse.json({
      snapshots: [],
      current_equity: 0
    });
  }),

  http.get(`${API_BASE}/api/graph/sentiment/:symbol`, () => {
    return HttpResponse.json({
      score: 0.5,
      label: "neutral",
      summary: "Market is stable"
    });
  }),

  http.get(`${API_BASE}/api/graph/crisis`, () => {
    return HttpResponse.json({
      active: false,
      level: 0,
      description: "No crisis detected"
    });
  }),

  http.get(`${API_BASE}/api/config`, () => {
    return HttpResponse.json({
      exchange: { paper_mode: true, leverage: 1, id: 'binance' },
      trading: { timeframe: '15m' },
      risk: { max_daily_loss_pct: 5, position_size_pct: 1 },
      notifications: { cooldown_secs: 60 }
    });
  }),

  http.get(`${API_BASE}/api/strategies/performance`, () => {
    return HttpResponse.json({
      performance: []
    });
  }),

  http.get(`${API_BASE}/api/env`, () => {
    return HttpResponse.json({
      VITE_API_URL: "http://localhost:8000"
    });
  }),

  http.get(`${API_BASE}/api/markets`, () => {
    return HttpResponse.json([
      { symbol: "BTC/USDT", base: "BTC", quote: "USDT", active: true },
      { symbol: "ETH/USDT", base: "ETH", quote: "USDT", active: true }
    ]);
  }),

  http.get(`${API_BASE}/api/graph/news`, () => {
    return HttpResponse.json([]);
  }),

  http.get(`${API_BASE}/api/graph/macro`, () => {
    return HttpResponse.json([]);
  }),

  http.get(`${API_BASE}/api/graph/correlation-matrix`, () => {
    return HttpResponse.json({
      symbols: ["BTC/USDT", "ETH/USDT"],
      matrix: [[1, 0.5], [0.5, 1]],
      timestamp: Date.now()
    });
  }),

  http.get(`${API_BASE}/api/candles/`, () => {
    return HttpResponse.json([]);
  }),
];
