import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useEffect, useState } from 'react';
import { fetchConfig, updateConfig } from '../lib/api';

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10 }}>
        {title}
      </div>
      <div className="grid-2">
        {children}
      </div>
    </div>
  )
}

function Field({
  label, value, onChange, type = 'text',
}: {
  label: string
  value: string | number
  onChange: (v: string) => void
  type?: string
}) {
  return (
    <div className="form-row">
      <label>{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)} />
    </div>
  )
}

export default function ConfigEditor() {
  const qc = useQueryClient()
  const { data: cfg, isLoading } = useQuery({ queryKey: ['config'], queryFn: fetchConfig })

  const [trading, setTrading] = useState<Record<string, string>>({})
  const [risk, setRisk] = useState<Record<string, string>>({})

  useEffect(() => {
    if (cfg) {
      setTrading({
        symbol: cfg.trading?.symbol ?? '',
        cycle_seconds: String(cfg.trading?.cycle_seconds ?? ''),
        position_size_pct: String(cfg.trading?.position_size_pct ?? ''),
      })
      setRisk({
        stop_loss_pct: String(cfg.risk?.stop_loss_pct ?? ''),
        take_profit_pct: String(cfg.risk?.take_profit_pct ?? ''),
        max_daily_loss_pct: String(cfg.risk?.max_daily_loss_pct ?? ''),
        max_positions: String(cfg.risk?.max_positions ?? ''),
      })
    }
  }, [cfg])

  const mutation = useMutation({
    mutationFn: () => {
      // Helper to convert string to number, but keep empty string as undefined (so it doesn't overwrite)
      const num = (v: string | undefined) => (v === '' || v === undefined ? undefined : Number(v))

      return updateConfig({
        trading: {
          symbol: trading.symbol || undefined,
          cycle_seconds: num(trading.cycle_seconds),
          position_size_pct: num(trading.position_size_pct),
        },
        risk: {
          stop_loss_pct: num(risk.stop_loss_pct),
          take_profit_pct: num(risk.take_profit_pct),
          max_daily_loss_pct: num(risk.max_daily_loss_pct),
          max_positions: num(risk.max_positions),
        },
      })
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['config'] }),
  })

  if (isLoading) return <div className="panel"><h2>Config</h2><p className="muted">Loading…</p></div>

  return (
    <div className="panel">
      <h2>Config</h2>

      <Section title="Trading">
        <Field label="Symbol" value={trading.symbol ?? ''} onChange={v => setTrading(p => ({ ...p, symbol: v }))} />
        <Field label="Cycle (seconds)" type="number" value={trading.cycle_seconds ?? ''} onChange={v => setTrading(p => ({ ...p, cycle_seconds: v }))} />
        <Field label="Position Size %" type="number" value={trading.position_size_pct ?? ''} onChange={v => setTrading(p => ({ ...p, position_size_pct: v }))} />
      </Section>

      <Section title="Risk">
        <Field label="Stop Loss %" type="number" value={risk.stop_loss_pct ?? ''} onChange={v => setRisk(p => ({ ...p, stop_loss_pct: v }))} />
        <Field label="Take Profit %" type="number" value={risk.take_profit_pct ?? ''} onChange={v => setRisk(p => ({ ...p, take_profit_pct: v }))} />
        <Field label="Max Daily Loss %" type="number" value={risk.max_daily_loss_pct ?? ''} onChange={v => setRisk(p => ({ ...p, max_daily_loss_pct: v }))} />
        <Field label="Max Positions" type="number" value={risk.max_positions ?? ''} onChange={v => setRisk(p => ({ ...p, max_positions: v }))} />
      </Section>

      <div className="form-actions">
        <button
          className="btn primary"
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Saving…' : 'Save Config'}
        </button>
        {mutation.isSuccess && <span style={{ color: 'var(--green)', fontSize: 12 }}>Saved ✓</span>}
        {mutation.isError && <span style={{ color: 'var(--red)', fontSize: 12 }}>Error saving</span>}
      </div>
    </div>
  )
}
