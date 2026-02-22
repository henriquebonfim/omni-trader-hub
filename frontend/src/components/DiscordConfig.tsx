import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchDiscordConfig, updateDiscordConfig, testDiscord } from '../lib/api'

export default function DiscordConfig() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['discordConfig'],
    queryFn: fetchDiscordConfig,
  })

  const [webhookUrl, setWebhookUrl] = useState('')
  const [enabled, setEnabled] = useState(true)
  const [testResult, setTestResult] = useState<string | null>(null)

  useEffect(() => {
    if (data) {
      setEnabled(data.enabled ?? true)
    }
  }, [data])

  const saveMut = useMutation({
    mutationFn: () => updateDiscordConfig({ webhook_url: webhookUrl, enabled }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['discordConfig'] }),
  })

  const testMut = useMutation({
    mutationFn: testDiscord,
    onSuccess: res => setTestResult(res.ok ? '✓ Message sent!' : `✗ ${res.message}`),
  })

  if (isLoading) return <div className="panel"><h2>Notifications</h2><p className="muted">Loading…</p></div>

  return (
    <div className="panel">
      <h2>Discord Notifications</h2>

      <div style={{ marginBottom: 12, fontSize: 12, color: 'var(--text-secondary)' }}>
        Current webhook: <span style={{ color: 'var(--text-muted)' }}>{data?.webhook_url_preview || 'Not configured'}</span>
        {' · '}
        <span className={`badge ${data?.enabled ? 'running' : 'stopped'}`} style={{ fontSize: 11 }}>
          {data?.enabled ? 'Enabled' : 'Disabled'}
        </span>
      </div>

      <div className="form-row">
        <label>New Webhook URL</label>
        <input
          type="url"
          placeholder="https://discord.com/api/webhooks/…"
          value={webhookUrl}
          onChange={e => setWebhookUrl(e.target.value)}
        />
      </div>

      <div className="form-row">
        <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={enabled}
            onChange={e => setEnabled(e.target.checked)}
            style={{ width: 'auto' }}
          />
          Enabled
        </label>
      </div>

      <div className="form-actions">
        <button
          className="btn primary"
          disabled={(!webhookUrl && !data?.configured) || saveMut.isPending}
          onClick={() => saveMut.mutate()}
        >
          {saveMut.isPending ? 'Saving…' : 'Save'}
        </button>
        <button
          className="btn"
          disabled={testMut.isPending}
          onClick={() => { setTestResult(null); testMut.mutate() }}
        >
          {testMut.isPending ? 'Sending…' : 'Test Webhook'}
        </button>
        {saveMut.isSuccess && <span style={{ color: 'var(--green)', fontSize: 12 }}>Saved ✓</span>}
        {testResult && (
          <span style={{ color: testResult.startsWith('✓') ? 'var(--green)' : 'var(--red)', fontSize: 12 }}>
            {testResult}
          </span>
        )}
      </div>
    </div>
  )
}
