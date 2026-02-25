import { useQuery } from '@tanstack/react-query'
import { fetchTrades } from '../lib/api'

function fmt(n: number | null | undefined, decimals = 2): string {
  if (n === null || n === undefined) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export default function SlippageReport() {
  const { data: tradesResponse, isLoading } = useQuery({
    queryKey: ['trades', 500],
    queryFn: () => fetchTrades(500)
  })

  const trades = tradesResponse?.trades || []

  // Filter trades with slippage data
  const slippageTrades = trades.filter((t: any) => t.slippage !== null && t.expected_price !== null)

  // Calculate stats
  const totalSlippage = slippageTrades.reduce((acc: number, t: any) => acc + (t.slippage || 0), 0)
  const avgSlippage = slippageTrades.length ? totalSlippage / slippageTrades.length : 0

  // Slippage % (Slippage / Expected Price)
  const slippagePcts = slippageTrades.map((t: any) => (t.slippage / t.expected_price) * 100)
  const avgSlippagePct = slippagePcts.length ? slippagePcts.reduce((a: number, b: number) => a + b, 0) / slippagePcts.length : 0
  const maxSlippagePct = slippagePcts.length ? Math.max(...slippagePcts) : 0
  const minSlippagePct = slippagePcts.length ? Math.min(...slippagePcts) : 0

  return (
    <div className="layout-col">
      <div className="panel">
        <h2>Slippage Report</h2>

        <div className="grid-4">
          <div className="stat">
            <span className="label">Trades Analyzed</span>
            <span className="value">{slippageTrades.length}</span>
          </div>
          <div className="stat">
            <span className="label">Avg Slippage %</span>
            <span className={`value ${avgSlippagePct > 0.1 ? 'red' : 'green'}`}>
              {fmt(avgSlippagePct, 4)}%
            </span>
          </div>
          <div className="stat">
            <span className="label">Max Slippage %</span>
            <span className="value red">
              {fmt(maxSlippagePct, 4)}%
            </span>
          </div>
          <div className="stat">
            <span className="label">Total Cost ($)</span>
            <span className="value">
              ${fmt(totalSlippage)}
            </span>
          </div>
        </div>

        <table className="table" style={{ marginTop: 20 }}>
          <thead>
            <tr>
              <th>Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Expected</th>
              <th>Actual</th>
              <th>Slippage</th>
              <th>%</th>
            </tr>
          </thead>
          <tbody>
            {slippageTrades.slice(0, 50).map((t: any) => {
              const slip = t.slippage
              const pct = (slip / t.expected_price) * 100
              const isBad = pct > 0.1 // > 0.1% slippage is bad

              return (
                <tr key={t.id}>
                  <td>{new Date(t.timestamp).toLocaleTimeString()}</td>
                  <td>{t.symbol}</td>
                  <td className={t.side === 'BUY' ? 'green' : 'red'}>{t.side}</td>
                  <td>{fmt(t.expected_price)}</td>
                  <td>{fmt(t.price)}</td>
                  <td className={slip > 0 ? 'red' : 'green'}>
                    {slip > 0 ? '+' : ''}{fmt(slip)}
                  </td>
                  <td className={isBad ? 'red' : ''}>
                    {fmt(pct, 4)}%
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {slippageTrades.length === 0 && !isLoading && (
          <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
            No slippage data available yet.
          </div>
        )}
      </div>
    </div>
  )
}
