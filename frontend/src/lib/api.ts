const BASE = '/api'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const apiKey = localStorage.getItem('omnitrader_api_key')
    const headers = new Headers(options.headers || {})
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    if (apiKey) {
      headers.set('Authorization', `Bearer ${apiKey}`)
    }

    const response = await fetch(url, { ...options, headers })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return response.json()
    }
    return response.text()
  }

  get(endpoint: string, params?: Record<string, any>) {
    let query = ''
    if (params) {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, String(value))
        }
      })
      query = `?${searchParams.toString()}`
    }
    return this.request(`${endpoint}${query}`)
  }

  post(endpoint: string, body?: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  put(endpoint: string, body?: any) {
    return this.request(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }
}

export const api = new ApiClient(BASE)

// Status
export const fetchStatus = () => api.get('/status')
export const fetchBalance = () => api.get('/balance')
export const fetchPosition = () => api.get('/position')

// Trades
export const fetchTrades = (limit = 50) => api.get('/trades', { limit })
export const fetchDailySummary = (date: string) => api.get(`/daily-summary/${date}`)
export const fetchEquity = (limit = 200) => api.get('/equity', { limit })

// Strategies
export const fetchStrategies = () => api.get('/strategies')

// Config
export const fetchConfig = () => api.get('/config')
export const updateConfig = (updates: object) => api.put('/config', updates)

// Bot control
export const botStart = () => api.post('/bot/start')
export const botStop = () => api.post('/bot/stop')
export const botRestart = () => api.post('/bot/restart')
export const fetchBotState = () => api.get('/bot/state')

// Notifications
export const fetchDiscordConfig = () => api.get('/notifications/discord')
export const updateDiscordConfig = (payload: { webhook_url: string; enabled: boolean }) =>
  api.put('/notifications/discord', payload)
export const testDiscord = () => api.post('/notifications/discord/test')

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
