import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { botRestart, botStart, botStop, fetchBotState } from '../lib/api'

function fmt(n: number, d = 2) {
  return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })
}

export default function BotControl() {
  const qc = useQueryClient()

  const { data: state, isLoading } = useQuery({
    queryKey: ['botState'],
    queryFn: fetchBotState,
    refetchInterval: 5000,
  })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['botState'] })
    qc.invalidateQueries({ queryKey: ['status'] })
  }

  const startMut  = useMutation({ mutationFn: botStart,   onSuccess: invalidate })
  const stopMut   = useMutation({ mutationFn: botStop,    onSuccess: invalidate })
  const restartMut = useMutation({ mutationFn: botRestart, onSuccess: invalidate })

  const pending = startMut.isPending || stopMut.isPending || restartMut.isPending
  const running = state?.running ?? false
  const cb = state?.circuit_breaker ?? false

  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ marginBottom: 0 }}>Bot Control</h2>
        {!isLoading && (
          <span className={`badge ${cb ? 'paused' : running ? 'running' : 'stopped'}`}>
            {cb ? 'Circuit Breaker' : running ? 'Running' : 'Stopped'}
          </span>
        )}
      </div>

      {!isLoading && state && (
        <div className="grid-3" style={{ marginBottom: 16 }}>
          <div className="stat">
            <span className="label">Daily PnL</span>
            <span className={`value ${state.daily_pnl >= 0 ? 'green' : 'red'}`}>
              ${fmt(state.daily_pnl)}
            </span>
          </div>
          <div className="stat">
            <span className="label">Trades Today</span>
            <span className="value">{state.trades_today}</span>
          </div>
          <div className="stat">
            <span className="label">Win / Loss</span>
            <span className="value">{state.wins} / {state.losses}</span>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 8 }}>
        <button
          className="btn success"
          disabled={pending || running}
          onClick={() => startMut.mutate()}
        >
          ▶ Start
        </button>
        <button
          className="btn danger"
          disabled={pending || !running}
          onClick={() => stopMut.mutate()}
        >
          ■ Stop
        </button>
        <button
          className="btn"
          disabled={pending}
          onClick={() => restartMut.mutate()}
        >
          ↺ Restart
        </button>
      </div>
    </div>
  )
}
