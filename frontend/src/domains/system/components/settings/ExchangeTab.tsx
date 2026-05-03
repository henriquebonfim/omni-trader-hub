import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { cn } from '@/core/utils';
import { request } from '@/core/api';
import { fetchSystemInfo, type SystemInfo } from '@/domains/system/api';
import type { AppConfig } from '@/domains/system/types';
import { SettingRow } from './SettingRow';

export function ExchangeTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
  const [exchangeAdapter, setExchangeAdapter] = useState<AppConfig['exchange_adapter']>(config.exchange_adapter);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'Connected' | 'Degraded' | 'Disconnected'>('Connected');
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [sysInfo, setSysInfo] = useState<SystemInfo | null>(null);

  useEffect(() => {
    setExchangeAdapter(config.exchange_adapter);
  }, [config]);

  useEffect(() => {
    fetchSystemInfo().then(setSysInfo).catch(console.error);
  }, []);

  const handleSaveExchange = async () => {
    setSaving(true);
    try {
      await onSave({ ...config, exchange_adapter: exchangeAdapter }, 'Exchange settings saved');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    const started = performance.now();
    try {
      await request('/api/health');
      const status = await request<{ running: boolean; total_bots?: number }>('/api/status');
      const elapsed = Math.round(performance.now() - started);
      setLatencyMs(elapsed);
      setConnectionStatus(status.running ? 'Connected' : 'Degraded');
      toast.success(`Connection OK (${elapsed}ms)`);
      // Refresh rate limit stats after test
      fetchSystemInfo().then(setSysInfo).catch(console.error);
    } catch {
      setConnectionStatus('Disconnected');
      setLatencyMs(null);
      toast.error('Connection test failed');
    } finally {
      setTesting(false);
    }
  };

  const rlUsed = sysInfo?.rate_limit_used ?? null;
  const rlCapacity = sysInfo?.rate_limit_capacity ?? 2000;
  const rlPct = rlUsed !== null ? ((rlUsed / rlCapacity) * 100).toFixed(1) : null;

  return (
    <Panel title="Exchange Connection">
      <div className="space-y-4 max-w-lg">
        <SettingRow label="Exchange Adapter">
          <div className="flex gap-2">
            {[
              { label: 'Binance Direct', value: 'binance' as const },
              { label: 'CCXT', value: 'ccxt' as const },
              { label: 'Auto-fallback', value: 'auto' as const },
            ].map(a => (
              <button key={a.label} onClick={() => setExchangeAdapter(a.value)} className={cn(
                'px-3 py-1.5 rounded-md border text-xs transition-colors',
                exchangeAdapter === a.value ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground'
              )}>{a.label}</button>
            ))}
          </div>
        </SettingRow>

        <div className="rounded-md border border-border p-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Connection Status</span>
            <StatusBadge variant={connectionStatus === 'Connected' ? 'success' : connectionStatus === 'Degraded' ? 'warning' : 'danger'} pulse={connectionStatus === 'Connected'} size="sm">{connectionStatus}</StatusBadge>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Latency</span>
            <span className={cn('font-mono', latencyMs !== null && latencyMs <= 150 ? 'text-success' : 'text-warning')}>{latencyMs !== null ? `${latencyMs}ms` : '—'}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Rate Limit Used</span>
            <span className={cn('font-mono', rlPct !== null && parseFloat(rlPct) > 70 ? 'text-warning' : 'text-foreground')}>
              {rlUsed !== null ? `${rlUsed} / ${rlCapacity}${rlPct ? ` (${rlPct}%)` : ''}` : '—'}
            </span>
          </div>
        </div>

        <div className="flex gap-2">
          <button onClick={handleTestConnection} disabled={testing} className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors disabled:opacity-60">
            {testing ? 'Testing…' : 'Test Connection'}
          </button>
          <button onClick={handleSaveExchange} disabled={saving} className="px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60">
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </Panel>
  );
}
