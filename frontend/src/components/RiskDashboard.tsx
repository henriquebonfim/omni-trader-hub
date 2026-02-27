import { useQuery } from '@tanstack/react-query'
import { fetchStatus, fetchDailySummary } from '../lib/api'
import { useLiveFeed } from '../lib/ws'
import PositionMonitor from './PositionMonitor'

function fmt(n: number | undefined | null, decimals = 2) {
  if (n === undefined || n === null) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export default function RiskDashboard() {
  const { message } = useLiveFeed()
  const { data: status } = useQuery({ queryKey: ['status'], queryFn: fetchStatus })

  // Get today's date YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0]
  const { data: daily } = useQuery({
    queryKey: ['dailySummary', today],
    queryFn: () => fetchDailySummary(today),
    retry: false
  })

  // Calculate drawdown (Daily PnL / Starting Balance)
  const drawdown = daily ? (daily.pnl / daily.starting_balance) * 100 : 0
  const maxDrawdown = 5.0 // Hardcoded from config default for display, ideally fetch config

  const cbActive = status?.circuit_breaker_active ?? false

  return (
    <div className="layout-col">
      <div className="grid-2">
        {/* Risk Overview Panel */}
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h2 style={{ marginBottom: 0 }}>Risk Overview</h2>
            {cbActive ? (
              <span className="badge paused">⚡ CIRCUIT BREAKER ACTIVE</span>
            ) : (
              <span className="badge running">Risk Checks Passing</span>
            )}
          </div>

          <div className="grid-2">
            <div className="stat">
              <span className="label">Daily PnL</span>
              <span className={`value ${daily?.pnl >= 0 ? 'green' : 'red'}`}>
                ${fmt(daily?.pnl)} ({fmt(daily?.pnl_pct)}%)
              </span>
            </div>
            <div className="stat">
              <span className="label">Max Daily Loss</span>
              <span className="value red">
                -{fmt(maxDrawdown)}%
              </span>
            </div>

            <div className="stat">
              <span className="label">Drawdown Usage</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  flex: 1,
                  height: 6,
                  background: 'var(--bg-lighter)',
                  borderRadius: 3,
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${Math.min(100, Math.abs(drawdown / maxDrawdown) * 100)}%`,
                    height: '100%',
                    background: Math.abs(drawdown) > maxDrawdown * 0.8 ? 'var(--red)' : 'var(--green)',
                    transition: 'width 0.5s'
                  }} />
                </div>
                <span style={{ fontSize: 12 }}>{fmt(Math.abs(drawdown / maxDrawdown) * 100, 0)}%</span>
              </div>
            </div>

            <div className="stat">
              <span className="label">Leverage</span>
              <span className="value">
                {status?.paper_mode ? '3x (Paper)' : '3x (Live)'}
              </span>
            </div>

            <div className="stat">
              <span className="label">Market Trend</span>
              <span className={`value ${message?.market_trend === 'bullish' ? 'green' : message?.market_trend === 'bearish' ? 'red' : ''}`}>
                {message?.market_trend?.toUpperCase() || '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Position Monitor Panel */}
        <PositionMonitor />
      </div>
    </div>
  )
}
