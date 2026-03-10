const BASE_URL = 'http://localhost:8000';

export async function fetchStatus() {
  const res = await fetch(`${BASE_URL}/api/status`);
  return res.json();
}

export async function startBot() {
  const res = await fetch(`${BASE_URL}/api/bot/start`, { method: 'POST' });
  return res.json();
}

export async function stopBot() {
  const res = await fetch(`${BASE_URL}/api/bot/stop`, { method: 'POST' });
  return res.json();
}

export async function fetchTradeHistory(limit = 50) {
  const res = await fetch(`${BASE_URL}/api/trades/history?limit=${limit}`);
  return res.json();
}

export async function fetchEquitySnapshots(days = 7) {
  const res = await fetch(`${BASE_URL}/api/equity/snapshots?days=${days}`);
  return res.json();
}

export async function fetchConfig() {
  const res = await fetch(`${BASE_URL}/api/config`);
  return res.json();
}

export async function updateConfig(config: Record<string, unknown>) {
  const res = await fetch(`${BASE_URL}/api/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return res.json();
}

export async function fetchSentiment(symbol: string) {
  const res = await fetch(`${BASE_URL}/api/graph/sentiment/${symbol}`);
  return res.json();
}

export async function fetchCrisisStatus() {
  const res = await fetch(`${BASE_URL}/api/graph/crisis`);
  return res.json();
}

export async function toggleCrisisMode(active: boolean) {
  const res = await fetch(`${BASE_URL}/api/graph/crisis`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ active }),
  });
  return res.json();
}

export async function fetchNews() {
  const res = await fetch(`${BASE_URL}/api/graph/news`);
  return res.json();
}

export async function runBacktest(config: Record<string, unknown>) {
  const res = await fetch(`${BASE_URL}/api/backtest/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return res.json();
}

export async function fetchBacktestResults(id: string) {
  const res = await fetch(`${BASE_URL}/api/backtest/results/${id}`);
  return res.json();
}
