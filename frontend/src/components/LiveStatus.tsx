import { useLiveFeed } from '../lib/ws'
import { useQuery } from '@tanstack/react-query'
import { fetchStatus } from '../lib/api'

function fmt(n: number, decimals = 2) {
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export default function LiveStatus() {
  const { message, status: wsStatus } = useLiveFeed()
  const { data: botStatus } = useQuery({ queryKey: ['status'], queryFn: fetchStatus })

  const price = message?.price ?? null
  const signal = message?.signal ?? '—'
  const position = message?.position ?? null
  const balance = message?.balance ?? null
  const dailyPnl = message?.daily_pnl ?? 0
  const dailyPnlPct = message?.daily_pnl_pct ?? 0
  const cb = message?.circuit_breaker ?? false

  const pnlClass = dailyPnl >= 0 ? 'pnl-pos' : 'pnl-neg'

  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ marginBottom: 0 }}>Live Feed</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: wsStatus === 'open' ? 'var(--green)' : 'var(--text-muted)' }}>
            WS {wsStatus}
          </span>
          {cb && <span className="badge stopped">⚡ Circuit Breaker</span>}
          {botStatus && (
            <span className={`badge ${botStatus.running ? 'running' : 'stopped'}`}>
              {botStatus.running ? 'Running' : 'Stopped'}
            </span>
          )}
        </div>
      </div>

      <div className="grid-4">
        <div className="stat">
          <span className="label">Price</span>
          <span className="value accent">{price !== null ? `$${fmt(price)}` : '—'}</span>
        </div>
        <div className="stat">
          <span className="label">Signal</span>
          <span className={`signal-badge ${signal}`} style={{ fontSize: 16, fontWeight: 600, padding: '4px 12px' }}>
            {signal}
          </span>
        </div>
        <div className="stat">
          <span className="label">Position</span>
          <span className={`badge ${position ?? 'flat'}`} style={{ fontSize: 14, padding: '4px 12px' }}>
            {position ? position.toUpperCase() : 'FLAT'}
          </span>
        </div>
        <div className="stat">
          <span className="label">Balance</span>
          <span className="value">{balance !== null ? `$${fmt(balance)}` : '—'}</span>
        </div>
      </div>

      <div className="grid-2" style={{ marginTop: 16 }}>
        <div className="stat">
          <span className="label">Daily PnL</span>
          <span className={`value ${pnlClass}`}>
            ${fmt(dailyPnl)} ({fmt(dailyPnlPct)}%)
          </span>
        </div>
        <div className="stat">
          <span className="label">Symbol</span>
          <span className="value">{botStatus?.symbol ?? '—'}</span>
        </div>
      </div>

      {message?.reason && (
        <p style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)' }}>
          Last reason: {message.reason}
        </p>
      )}
    </div>
  )
}
