import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import {
    fetchConfig,
    fetchEnvVars,
    fetchNotificationRules,
    updateConfig,
    updateNotificationRules,
} from '@/domains/system/api';
import type { EnvVariable, NotificationRules } from '@/domains/system/types';
import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { AlertTriangle, Eye, EyeOff, RotateCcw, Save, Send } from 'lucide-react';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

type SettingsTab = 'general' | 'environment' | 'risk' | 'notifications' | 'exchange' | 'system';

export default function SettingsPage() {
  const [tab, setTab] = useState<SettingsTab>('general');
  const config = useAppStore(s => s.config);
  const setConfig = useAppStore(s => s.updateConfig);
  const [envVars, setEnvVars] = useState<EnvVariable[]>([]);

  useEffect(() => {
    fetchConfig().then(data => setConfig(data)).catch(console.error);
    fetchEnvVars().then(setEnvVars).catch(console.error);
  }, [setConfig]);

  const handleSaveConfig = async () => {
    try {
      await updateConfig(config);
      toast.success('Configuration saved');
    } catch (e) {
      toast.error('Failed to save configuration');
    }
  };

  const tabs: { key: SettingsTab; label: string }[] = [
    { key: 'general', label: 'General' },
    { key: 'environment', label: 'Environment' },
    { key: 'risk', label: 'Risk Defaults' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'exchange', label: 'Exchange' },
    { key: 'system', label: 'System' },
  ];

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Settings</h1>

      {/* Tabs */}
      <div className="flex border-b border-border overflow-x-auto">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={cn(
              'px-4 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap',
              tab === t.key ? 'border-accent text-accent' : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

        {tab === 'general' && <GeneralTab config={config} />}
        {tab === 'environment' && <EnvironmentTab envVars={envVars} />}
        {tab === 'risk' && <RiskTab config={config} />}
        {tab === 'notifications' && <NotificationsTab config={config} />}
        {tab === 'exchange' && <ExchangeTab config={config} />}
      {tab === 'system' && <SystemTab />}
    </div>
  );
}

import type { AppConfig } from '@/domains/system/types';

function GeneralTab({ config }: { config: AppConfig }) {
  const [mode, setMode] = useState<'paper' | 'live'>(config.mode);
  const [leverage, setLeverage] = useState(config.default_leverage);
  const [posSize, setPosSize] = useState(config.default_position_size_pct);
  const [autoStrategy, setAutoStrategy] = useState(config.auto_strategy_mode);
  const [timeframe, setTimeframe] = useState(config.default_timeframe);

  useEffect(() => {
    setMode(config.mode);
    setLeverage(config.default_leverage);
    setPosSize(config.default_position_size_pct);
    setAutoStrategy(config.auto_strategy_mode);
    setTimeframe(config.default_timeframe);
  }, [config]);

  return (
    <Panel title="General Settings">
      <div className="space-y-5 max-w-lg">
        <SettingRow label="Trading Mode" description="Paper mode uses simulated execution">
          <div className="flex gap-2">
            {(['paper', 'live'] as const).map(m => (
              <button key={m} onClick={() => setMode(m)} className={cn(
                'px-3 py-1.5 rounded-md border text-xs font-medium capitalize transition-colors',
                mode === m ? (m === 'live' ? 'border-danger bg-danger/10 text-danger' : 'border-accent bg-accent/10 text-accent') : 'border-border text-muted-foreground'
              )}>{m}</button>
            ))}
          </div>
        </SettingRow>

        <SettingRow label="Default Timeframe">
          <div className="flex gap-1">
            {['5m', '15m', '1h', '4h'].map(t => (
              <button key={t} onClick={() => setTimeframe(t)} className={cn(
                'px-2.5 py-1 rounded-md border text-xs transition-colors',
                timeframe === t ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground'
              )}>{t}</button>
            ))}
          </div>
        </SettingRow>

        <SettingRow label={`Default Leverage: ${leverage}×`}>
          <input type="range" min={1} max={10} value={leverage} onChange={e => setLeverage(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>

        <SettingRow label={`Default Position Size: ${posSize}%`}>
          <input type="range" min={1} max={20} value={posSize} onChange={e => setPosSize(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>

        <SettingRow label="Auto-Strategy Mode" description="Bots autonomously select strategies based on regime">
          <button onClick={() => setAutoStrategy(!autoStrategy)} className={cn(
            'relative w-10 h-5 rounded-full transition-colors',
            autoStrategy ? 'bg-accent' : 'bg-secondary'
          )}>
            <span className={cn('absolute top-0.5 w-4 h-4 rounded-full bg-foreground transition-transform', autoStrategy ? 'left-5' : 'left-0.5')} />
          </button>
        </SettingRow>

        <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors">
          <Save className="h-3.5 w-3.5" /> Save Changes
        </button>
      </div>
    </Panel>
  );
}

function EnvironmentTab({ envVars }: { envVars: EnvVariable[] }) {
  const [vars, setVars] = useState(envVars);
  const [revealed, setRevealed] = useState<Set<string>>(new Set());

  useEffect(() => {
    setVars(envVars);
  }, [envVars]);

  const toggleReveal = (key: string) => {
    const next = new Set(revealed);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    setRevealed(next);
  };

  const categories = [...new Set(vars.map(v => v.category))];

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-warning/30 bg-warning/5 p-3 flex items-center gap-3">
        <AlertTriangle className="h-4 w-4 text-warning shrink-0" />
        <p className="text-xs text-warning">Changes marked with 🔄 require a service restart to take effect.</p>
      </div>

      {categories.map(cat => (
        <Panel key={cat} title={cat}>
          <div className="space-y-3">
            {vars.filter(v => v.category === cat).map(v => (
              <div key={v.key} className="flex items-center gap-3">
                <div className="w-48 shrink-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-mono font-medium">{v.key}</span>
                    {v.requires_restart && <span className="text-[10px]">🔄</span>}
                  </div>
                  <p className="text-[10px] text-muted-foreground">{v.description}</p>
                </div>
                <div className="flex-1 flex items-center gap-2">
                  <input
                    type={v.masked && !revealed.has(v.key) ? 'password' : 'text'}
                    value={v.value}
                    onChange={e => setVars(vars.map(ev => ev.key === v.key ? { ...ev, value: e.target.value } : ev))}
                    className="w-full px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent"
                  />
                  {v.masked && (
                    <button onClick={() => toggleReveal(v.key)} className="p-1.5 rounded hover:bg-secondary transition-colors">
                      {revealed.has(v.key) ? <EyeOff className="h-3.5 w-3.5 text-muted-foreground" /> : <Eye className="h-3.5 w-3.5 text-muted-foreground" />}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      ))}

      <div className="flex gap-2">
        <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors">
          <Save className="h-3.5 w-3.5" /> Save Changes
        </button>
        <button className="flex items-center gap-2 px-4 py-2 rounded-md border border-warning/50 text-warning text-xs font-medium hover:bg-warning/10 transition-colors">
          <RotateCcw className="h-3.5 w-3.5" /> Restart Services
        </button>
      </div>
    </div>
  );
}

function RiskTab({ config }: { config: AppConfig }) {
  return (
    <Panel title="Risk Defaults">
      <div className="space-y-4 max-w-lg">
        <SettingRow label="Max Daily Loss: 5%">
          <input type="range" min={1} max={20} defaultValue={5} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label="Max Weekly Loss: 10%">
          <input type="range" min={1} max={30} defaultValue={10} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label="Consecutive Loss Limit: 3">
          <input type="range" min={1} max={10} defaultValue={3} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label="Stop Loss Mode">
          <div className="flex gap-2">
            <button className="px-3 py-1.5 rounded-md border border-accent bg-accent/10 text-accent text-xs">ATR Multiplier</button>
            <button className="px-3 py-1.5 rounded-md border border-border text-muted-foreground text-xs">Fixed %</button>
          </div>
        </SettingRow>
        <SettingRow label="Black Swan Threshold: 10%">
          <input type="range" min={5} max={25} defaultValue={10} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label="Auto-Deleverage Drawdown: 15%">
          <input type="range" min={5} max={30} defaultValue={15} className="w-full accent-accent" />
        </SettingRow>
        <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold">
          <Save className="h-3.5 w-3.5" /> Save
        </button>
      </div>
    </Panel>
  );
}

function NotificationsTab({ config }: { config: AppConfig }) {
  const [rules, setRules] = useState<NotificationRules>({
    circuit_breaker: true,
    strategy_rotation: true,
    regime_change: true,
    pnl_thresholds: true,
    pnl_warning_pct: 3.0,
    pnl_critical_pct: 5.0,
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchNotificationRules()
      .then(setRules)
      .catch(() => {
        // Keep fallback defaults in local state if API is temporarily unavailable.
      });
  }, [config]);

  const toggleRule = (key: keyof NotificationRules) => {
    if (typeof rules[key] !== 'boolean') return;
    setRules((prev) => ({ ...prev, [key]: !(prev[key] as boolean) }));
  };

  const handleSaveRules = async () => {
    setSaving(true);
    try {
      const normalized: NotificationRules = {
        ...rules,
        pnl_warning_pct: Number(rules.pnl_warning_pct),
        pnl_critical_pct: Math.max(Number(rules.pnl_critical_pct), Number(rules.pnl_warning_pct)),
      };
      await updateNotificationRules(normalized);
      setRules(normalized);
      toast.success('Notification rules saved');
    } catch {
      toast.error('Failed to save notification rules');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Panel title="Notification Settings">
      <div className="space-y-4 max-w-lg">
        <SettingRow label="Discord Webhook URL">
          <div className="flex gap-2">
            <input type="password" defaultValue="https://discord.com/api/webhooks/..." className="flex-1 px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent" />
            <button className="px-3 py-1.5 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors flex items-center gap-1">
              <Send className="h-3 w-3" /> Test
            </button>
          </div>
        </SettingRow>

        {Object.entries({
          circuit_breaker: 'Circuit Breaker Alerts',
          strategy_rotation: 'Strategy Rotation Alerts',
          regime_change: 'Regime Change Alerts',
          pnl_thresholds: 'PnL Threshold Alerts',
        }).map(([key, label]) => (
          <SettingRow key={key} label={label}>
            <button
              onClick={() => toggleRule(key as keyof NotificationRules)}
              className={cn('w-10 h-5 rounded-full relative transition-colors', rules[key as keyof NotificationRules] ? 'bg-accent' : 'bg-secondary')}
            >
              <span className={cn('absolute top-0.5 w-4 h-4 rounded-full bg-foreground transition-transform', rules[key as keyof NotificationRules] ? 'left-5' : 'left-0.5')} />
            </button>
          </SettingRow>
        ))}

        <SettingRow label="PnL Warning Threshold (%)">
          <input
            type="number"
            min={0.1}
            step={0.1}
            value={rules.pnl_warning_pct}
            onChange={(e) => setRules((prev) => ({ ...prev, pnl_warning_pct: Number(e.target.value) || 0.1 }))}
            className="w-28 px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </SettingRow>

        <SettingRow label="PnL Critical Threshold (%)">
          <input
            type="number"
            min={0.1}
            step={0.1}
            value={rules.pnl_critical_pct}
            onChange={(e) => setRules((prev) => ({ ...prev, pnl_critical_pct: Number(e.target.value) || 0.1 }))}
            className="w-28 px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </SettingRow>

        <button
          onClick={handleSaveRules}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold disabled:opacity-60"
        >
          <Save className="h-3.5 w-3.5" /> Save
        </button>
      </div>
    </Panel>
  );
}

function ExchangeTab({ config }: { config: AppConfig }) {
  return (
    <Panel title="Exchange Connection">
      <div className="space-y-4 max-w-lg">
        <SettingRow label="Exchange Adapter">
          <div className="flex gap-2">
            {['Binance Direct', 'CCXT', 'Auto-fallback'].map(a => (
              <button key={a} className={cn(
                'px-3 py-1.5 rounded-md border text-xs transition-colors',
                a === 'Binance Direct' ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground'
              )}>{a}</button>
            ))}
          </div>
        </SettingRow>

        <div className="rounded-md border border-border p-3 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Connection Status</span>
            <StatusBadge variant="success" pulse size="sm">Connected</StatusBadge>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Latency</span>
            <span className="font-mono text-success">42ms</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Success Rate</span>
            <span className="font-mono">99.8%</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Rate Limit</span>
            <span className="font-mono">42 / 1200</span>
          </div>
        </div>

        <button className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors">
          Test Connection
        </button>
      </div>
    </Panel>
  );
}

function SystemTab() {
  const services = [
    { name: 'omnitrader', status: 'running' },
    { name: 'memgraph', status: 'running' },
    { name: 'redis', status: 'running' },
    { name: 'ollama', status: 'running' },
  ];

  return (
    <div className="space-y-4">
      <Panel title="Docker Services">
        <div className="space-y-2">
          {services.map(s => (
            <div key={s.name} className="flex items-center justify-between rounded-md border border-border/50 p-3">
              <span className="text-xs font-mono font-medium">{s.name}</span>
              <StatusBadge variant={s.status === 'running' ? 'success' : 'danger'} pulse={s.status === 'running'} size="sm">
                {s.status}
              </StatusBadge>
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="System Info">
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-muted-foreground">Memgraph Nodes</span><span className="font-mono">1,247</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Memgraph Relationships</span><span className="font-mono">3,891</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Redis Memory</span><span className="font-mono">24.5 MB</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Ollama Model</span><span className="font-mono">llama3.1:8b</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Version</span><span className="font-mono">v2.4.1</span></div>
        </div>
      </Panel>

      <div className="flex gap-2">
        <button className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors">
          Backup Database
        </button>
        <button className="px-4 py-2 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors">
          View Logs
        </button>
      </div>
    </div>
  );
}

function SettingRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <div>
        <label className="text-xs font-medium">{label}</label>
        {description && <p className="text-[10px] text-muted-foreground">{description}</p>}
      </div>
      {children}
    </div>
  );
}
