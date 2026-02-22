import axios from 'axios'

const BASE = '/api'

export const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
})

// Status
export const fetchStatus = () => api.get('/status').then(r => r.data)
export const fetchBalance = () => api.get('/balance').then(r => r.data)
export const fetchPosition = () => api.get('/position').then(r => r.data)

// Trades
export const fetchTrades = (limit = 50) =>
  api.get('/trades', { params: { limit } }).then(r => r.data)
export const fetchDailySummary = (date: string) =>
  api.get(`/daily-summary/${date}`).then(r => r.data)
export const fetchEquity = (limit = 200) =>
  api.get('/equity', { params: { limit } }).then(r => r.data)

// Strategies
export const fetchStrategies = () => api.get('/strategies').then(r => r.data)

// Config
export const fetchConfig = () => api.get('/config').then(r => r.data)
export const updateConfig = (updates: object) => api.put('/config', updates).then(r => r.data)

// Bot control
export const botStart = () => api.post('/bot/start').then(r => r.data)
export const botStop = () => api.post('/bot/stop').then(r => r.data)
export const botRestart = () => api.post('/bot/restart').then(r => r.data)
export const fetchBotState = () => api.get('/bot/state').then(r => r.data)

// Notifications
export const fetchDiscordConfig = () => api.get('/notifications/discord').then(r => r.data)
export const updateDiscordConfig = (payload: { webhook_url: string; enabled: boolean }) =>
  api.put('/notifications/discord', payload).then(r => r.data)
export const testDiscord = () => api.post('/notifications/discord/test').then(r => r.data)

// Types
export interface Trade {
  id: number
  timestamp: string
  symbol: string
  side: string
  action: string
  price: number
  size: number
  notional: number
  pnl: number | null
  pnl_pct: number | null
  reason: string | null
  stop_loss: number | null
  take_profit: number | null
}

export interface EquitySnapshot {
  id: number
  timestamp: string
  balance: number
}

export interface CycleMessage {
  type: 'cycle'
  timestamp: string
  symbol: string
  price: number
  signal: string
  reason: string
  indicators: Record<string, number>
  position: string | null
  balance: number
  daily_pnl: number
  daily_pnl_pct: number
  circuit_breaker: boolean
}
