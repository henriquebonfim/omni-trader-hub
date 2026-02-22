import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { fetchStrategies, updateConfig } from '../lib/api'

export default function StrategySelector() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['strategies'],
    queryFn: fetchStrategies,
  })

  const mutation = useMutation({
    mutationFn: (name: string) => updateConfig({ strategy: { name } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['strategies'] })
      qc.invalidateQueries({ queryKey: ['config'] })
    },
  })

  const strategies = data?.strategies ?? []
  const active = data?.active ?? ''
  const [selected, setSelected] = useState('')
  const current = selected || active

  return (
    <div className="panel">
      <h2>Strategy</h2>
      {isLoading ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <div className="form-row">
            <label>Active Strategy</label>
            <select
              value={current}
              onChange={e => setSelected(e.target.value)}
            >
              {strategies.map((s: { name: string; active: boolean }) => (
                <option key={s.name} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {strategies
            .filter((s: { name: string; metadata: Record<string, string> }) => s.name === current)
            .map((s: { name: string; metadata: Record<string, string> }) => (
              <div key={s.name} style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>
                {Object.entries(s.metadata).map(([k, v]) => (
                  <div key={k}>
                    <span style={{ color: 'var(--text-muted)' }}>{k}: </span>
                    {String(v)}
                  </div>
                ))}
              </div>
            ))}

          <div className="form-actions">
            <button
              className="btn primary"
              disabled={current === active || mutation.isPending}
              onClick={() => mutation.mutate(current)}
            >
              {mutation.isPending ? 'Saving…' : 'Apply Strategy'}
            </button>
            {mutation.isSuccess && (
              <span style={{ color: 'var(--green)', fontSize: 12 }}>Saved ✓</span>
            )}
          </div>
        </>
      )}
    </div>
  )
}
