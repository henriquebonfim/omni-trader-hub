import { useQuery } from '@tanstack/react-query'
import { fetchPosition } from '../lib/api'
import { useLiveFeed } from '../lib/ws'

function fmt(n: number | null | undefined, decimals = 2): string {
  if (n === null || n === undefined) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function formatDuration(seconds: number | undefined) {
  if (seconds === undefined || seconds === null) return '—'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${h}h ${m}m ${s}s`
}

export default function PositionMonitor() {
  const { message } = useLiveFeed()
  const price = message?.price

  const { data: pos } = useQuery({
    queryKey: ['position'],
    queryFn: fetchPosition,
    refetchInterval: 5000 // Poll every 5s
  })

  if (!pos || !pos.is_open) {
    return (
      <div className="panel">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h2 style={{ marginBottom: 0 }}>Position Monitor</h2>
          <span className="badge stopped">Flat</span>
        </div>
        <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)' }}>
          No active position
        </div>
      </div>
    )
  }

  const pnlClass = (pos.unrealized_pnl || 0) >= 0 ? 'pnl-pos' : 'pnl-neg'

  // Calculate liquidation distance
  let liqDistPct = 0
  if (price && pos.liquidation_price) {
    liqDistPct = (Math.abs(price - pos.liquidation_price) / price) * 100
  }

  // Safety zones for liquidation distance
  let liqColor = 'var(--green)'
  if (liqDistPct < 1.0) liqColor = 'var(--red)'
  else if (liqDistPct < 5.0) liqColor = 'var(--orange)'

  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ marginBottom: 0 }}>Position Monitor</h2>
        <span className={`badge ${pos.side === 'long' ? 'running' : 'stopped'}`}>
          {pos.side ? pos.side.toUpperCase() : ''} {pos.leverage}x
        </span>
      </div>

      <div className="grid-2">
        <div className="stat">
          <span className="label">Symbol</span>
          <span className="value">{pos.symbol}</span>
        </div>
        <div className="stat">
          <span className="label">Entry Price</span>
          <span className="value">${fmt(pos.entry_price)}</span>
        </div>

        <div className="stat">
          <span className="label">Size</span>
          <span className="value">{pos.size} ({fmt(pos.notional)} USDT)</span>
        </div>
        <div className="stat">
          <span className="label">Mark Price</span>
          <span className="value accent">${fmt(price)}</span>
        </div>

        <div className="stat">
          <span className="label">Time in Trade</span>
          <span className="value">{formatDuration(message?.time_in_trade)}</span>
        </div>

        <div className="stat">
          <span className="label">Unrealized PnL</span>
          <span className={`value ${pnlClass}`}>
            ${fmt(pos.unrealized_pnl)}
          </span>
        </div>
        <div className="stat">
          <span className="label">Liq Distance</span>
          <span className="value" style={{ color: liqColor }}>
            {fmt(liqDistPct)}%
          </span>
        </div>

        <div className="stat">
          <span className="label">Liquidation Price</span>
          <span className="value" style={{ color: 'var(--red)' }}>${fmt(pos.liquidation_price)}</span>
        </div>
      </div>

      {/* Liquidation Bar */}
      {price && pos.liquidation_price > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4, color: 'var(--text-muted)' }}>
            <span>Liq: ${fmt(pos.liquidation_price)}</span>
            <span>Current: ${fmt(price)}</span>
          </div>
          <div style={{
            height: 8,
            background: 'var(--bg-lighter)',
            borderRadius: 4,
            overflow: 'hidden',
            position: 'relative'
          }}>
            {/*
              Visual approximation:
              We want to show how close current price is to liquidation price relative to entry.
              Distance = |Current - Liq|
              Max Range = |Entry - Liq|
              Percent = Distance / Range
            */}
            <div style={{
              width: `${Math.min(100, Math.max(0, (liqDistPct / (Math.abs(pos.entry_price - pos.liquidation_price)/pos.entry_price*100)) * 100))}%`,
              height: '100%',
              background: liqColor,
              transition: 'width 0.5s',
              opacity: 0.8
            }} />
          </div>
        </div>
      )}
    </div>
  )
}
