import { useQuery } from '@tanstack/react-query'
import { fetchEquity, type EquitySnapshot } from '../lib/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

function shortTs(ts: string) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function EquityCurve() {
  const { data, isLoading } = useQuery({
    queryKey: ['equity'],
    queryFn: () => fetchEquity(200),
  })

  const snapshots: EquitySnapshot[] = data?.snapshots ?? []

  const chartData = snapshots.map(s => ({
    time: shortTs(s.timestamp),
    balance: s.balance,
  }))

  const first = snapshots[0]?.balance ?? 0
  const last = snapshots[snapshots.length - 1]?.balance ?? 0
  const change = last - first
  const changeClass = change >= 0 ? 'pnl-pos' : 'pnl-neg'

  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <h2 style={{ marginBottom: 0 }}>Equity Curve</h2>
        {snapshots.length > 0 && (
          <span className={changeClass} style={{ fontSize: 13 }}>
            ${change >= 0 ? '+' : ''}{change.toFixed(2)}
          </span>
        )}
      </div>
      {isLoading ? (
        <p className="muted">Loading…</p>
      ) : snapshots.length === 0 ? (
        <p className="muted">No snapshots yet. Data appears after first cycle.</p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis
              dataKey="time"
              tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
              domain={['auto', 'auto']}
              tickFormatter={(v: number) => `$${v.toFixed(0)}`}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-panel)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                fontSize: 12,
              }}
              formatter={(v: number) => [`$${v.toFixed(2)}`, 'Balance']}
            />
            <Line
              type="monotone"
              dataKey="balance"
              stroke="var(--accent)"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
