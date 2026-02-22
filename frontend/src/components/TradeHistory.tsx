import { useQuery } from '@tanstack/react-query'
import { fetchTrades, type Trade } from '../lib/api'

function fmt(n: number | null, decimals = 2) {
  if (n == null) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function shortTs(ts: string) {
  return new Date(ts).toLocaleString()
}

export default function TradeHistory() {
  const { data, isLoading } = useQuery({
    queryKey: ['trades'],
    queryFn: () => fetchTrades(50),
  })

  const trades: Trade[] = data?.trades ?? []

  return (
    <div className="panel">
      <h2>Trade History</h2>
      {isLoading ? (
        <p className="muted">Loading…</p>
      ) : trades.length === 0 ? (
        <p className="muted">No trades yet.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Action</th>
                <th>Price</th>
                <th>Size</th>
                <th>Notional</th>
                <th>PnL</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {trades.map(t => {
                const pnlClass =
                  t.pnl == null ? '' : t.pnl >= 0 ? 'pnl-pos' : 'pnl-neg'
                return (
                  <tr key={t.id}>
                    <td className="muted">{shortTs(t.timestamp)}</td>
                    <td>{t.symbol}</td>
                    <td>
                      <span className={`badge ${t.side.toLowerCase()}`}>
                        {t.side}
                      </span>
                    </td>
                    <td>{t.action}</td>
                    <td>${fmt(t.price)}</td>
                    <td>{fmt(t.size, 4)}</td>
                    <td>${fmt(t.notional)}</td>
                    <td className={pnlClass}>
                      {t.pnl != null
                        ? `$${fmt(t.pnl)} (${fmt(t.pnl_pct)}%)`
                        : '—'}
                    </td>
                    <td className="muted">{t.reason ?? '—'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
