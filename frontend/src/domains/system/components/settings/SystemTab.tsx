import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import {
  backupDatabase,
  fetchStatusSummary,
  fetchSystemInfo,
  type SystemInfo,
} from '@/domains/system/api';

export function SystemTab() {
  const [info, setInfo] = useState<SystemInfo | null>(null);
  const [backingUp, setBackingUp] = useState(false);

  useEffect(() => {
    fetchSystemInfo().then(setInfo).catch(console.error);
    fetchStatusSummary().then(status => {
      setInfo(prev => prev ? { ...prev, services: { ...prev.services, omnitrader: status.running ? 'running' : 'stopped' } } : prev);
    }).catch(console.error);
  }, []);

  const SERVICE_NAMES = ['omnitrader', 'memgraph', 'redis', 'ollama'] as const;

  const handleBackup = async () => {
    setBackingUp(true);
    try {
      const res = await backupDatabase();
      toast.success(`Backup created at ${new Date(res.timestamp).toLocaleTimeString()}`);
    } catch {
      toast.error('Backup failed — check Memgraph connection');
    } finally {
      setBackingUp(false);
    }
  };

  const handleViewLogs = () => {
    if (!info) return;
    const lines = [
      `OmniTrader ${info.version}`,
      `Uptime: ${Math.floor(info.uptime_seconds / 3600)}h ${Math.floor((info.uptime_seconds % 3600) / 60)}m`,
      `Memgraph nodes: ${info.node_count.toLocaleString()}`,
      `Memgraph relationships: ${info.relationship_count.toLocaleString()}`,
      `Rate limit: ${info.rate_limit_used} / ${info.rate_limit_capacity}`,
      `Ollama model: ${info.ollama_model}`,
    ].join('\n');
    toast.info(lines, { duration: 8000 });
  };

  const formatUptime = (s: number) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  };

  return (
    <div className="space-y-4">
      <Panel title="Docker Services">
        <div className="space-y-2">
          {SERVICE_NAMES.map(name => {
            const status = info?.services?.[name] ?? 'unknown';
            return (
              <div key={name} className="flex items-center justify-between rounded-md border border-border/50 p-3">
                <span className="text-xs font-mono font-medium">{name}</span>
                <StatusBadge
                  variant={status === 'running' ? 'success' : status === 'stopped' ? 'danger' : 'warning'}
                  pulse={status === 'running'}
                  size="sm"
                >
                  {info ? status : 'loading…'}
                </StatusBadge>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel title="System Info">
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-muted-foreground">Memgraph Nodes</span><span className="font-mono">{info ? info.node_count.toLocaleString() : '—'}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Memgraph Relationships</span><span className="font-mono">{info ? info.relationship_count.toLocaleString() : '—'}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Rate Limit Used</span><span className="font-mono">{info ? `${info.rate_limit_used} / ${info.rate_limit_capacity}` : '—'}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Uptime</span><span className="font-mono">{info ? formatUptime(info.uptime_seconds) : '—'}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Ollama Model</span><span className="font-mono">{info?.ollama_model ?? '—'}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Version</span><span className="font-mono">{info?.version ?? '—'}</span></div>
        </div>
      </Panel>

      <div className="flex gap-2">
        <button
          onClick={handleBackup}
          disabled={backingUp}
          className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors disabled:opacity-60"
        >
          {backingUp ? 'Backing up…' : 'Backup Database'}
        </button>
        <button
          onClick={handleViewLogs}
          className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors"
        >
          View Logs
        </button>
      </div>
    </div>
  );
}
