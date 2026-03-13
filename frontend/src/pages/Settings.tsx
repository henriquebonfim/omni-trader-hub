import { useAppStore } from '@/app/store/app-store';
import { request } from '@/core/api';
import { cn } from '@/core/utils';
import {
  backupDatabase,
  fetchConfig,
  fetchDiscordWebhook,
  fetchEnvVars,
  fetchNotificationRules,
  fetchStatusSummary,
  fetchSystemInfo,
  restartSystem,
  testDiscordWebhook,
  updateConfig,
  updateDiscordWebhook,
  updateEnvVars,
  updateNotificationRules,
  type SystemInfo,
} from '@/domains/system/api';
import type { AppConfig, EnvVariable, NotificationRules } from '@/domains/system/types';
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

  const handleSaveConfig = async (nextConfig: AppConfig, successMessage = 'Configuration saved') => {
    try {
      await updateConfig(nextConfig);
      setConfig(nextConfig);
      toast.success(successMessage);
    } catch (e) {
      toast.error('Failed to save configuration');
    }
  };

  const handleRestartServices = async () => {
    if (!window.confirm('Restart backend services now? This may briefly interrupt API responses.')) {
      return;
    }
    try {
      await restartSystem();
      toast.success('Restart requested');
    } catch {
      toast.error('Failed to restart services');
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

        {tab === 'general' && <GeneralTab config={config} onSave={handleSaveConfig} />}
        {tab === 'environment' && <EnvironmentTab envVars={envVars} onRestart={handleRestartServices} />}
        {tab === 'risk' && <RiskTab config={config} onSave={handleSaveConfig} />}
        {tab === 'notifications' && <NotificationsTab config={config} />}
        {tab === 'exchange' && <ExchangeTab config={config} onSave={handleSaveConfig} />}
      {tab === 'system' && <SystemTab />}
    </div>
  );
}

function GeneralTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
  const [mode, setMode] = useState<'paper' | 'live'>(config.mode);
  const [leverage, setLeverage] = useState(config.default_leverage);
  const [posSize, setPosSize] = useState(config.default_position_size_pct);
  const [autoStrategy, setAutoStrategy] = useState(config.auto_strategy_mode);
  const [timeframe, setTimeframe] = useState(config.default_timeframe);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setMode(config.mode);
    setLeverage(config.default_leverage);
    setPosSize(config.default_position_size_pct);
    setAutoStrategy(config.auto_strategy_mode);
    setTimeframe(config.default_timeframe);
  }, [config]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(
        {
          ...config,
          mode,
          default_leverage: leverage,
          default_position_size_pct: posSize,
          auto_strategy_mode: autoStrategy,
          default_timeframe: timeframe,
        },
        'General settings saved'
      );
    } finally {
      setSaving(false);
    }
  };

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

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60"
        >
          <Save className="h-3.5 w-3.5" /> {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </div>
    </Panel>
  );
}

function EnvironmentTab({ envVars, onRestart }: { envVars: EnvVariable[]; onRestart: () => Promise<void> }) {
  const [vars, setVars] = useState(envVars);
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);

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

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await updateEnvVars(vars);
      toast.success(result.requires_restart ? 'Saved — service restart required' : 'Environment variables saved');
    } catch {
      toast.error('Failed to save environment variables');
    } finally {
      setSaving(false);
    }
  };

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
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60"
        >
          <Save className="h-3.5 w-3.5" /> {saving ? 'Saving…' : 'Save Changes'}
        </button>
        <button onClick={onRestart} className="flex items-center gap-2 px-4 py-2 rounded-md border border-warning/50 text-warning text-xs font-medium hover:bg-warning/10 transition-colors">
          <RotateCcw className="h-3.5 w-3.5" /> Restart Services
        </button>
      </div>
    </div>
  );
}

function RiskTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
  const [maxDailyLoss, setMaxDailyLoss] = useState(config.max_daily_loss_pct);
  const [maxWeeklyLoss, setMaxWeeklyLoss] = useState(config.max_weekly_loss_pct);
  const [consecutiveLossLimit, setConsecutiveLossLimit] = useState(config.consecutive_loss_limit);
  const [stopLossMode, setStopLossMode] = useState<AppConfig['stop_loss_mode']>(config.stop_loss_mode);
  const [blackSwanThreshold, setBlackSwanThreshold] = useState(config.black_swan_threshold);
  const [autoDeleverageDrawdown, setAutoDeleverageDrawdown] = useState(config.auto_deleverage_drawdown_pct);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setMaxDailyLoss(config.max_daily_loss_pct);
    setMaxWeeklyLoss(config.max_weekly_loss_pct);
    setConsecutiveLossLimit(config.consecutive_loss_limit);
    setStopLossMode(config.stop_loss_mode);
    setBlackSwanThreshold(config.black_swan_threshold);
    setAutoDeleverageDrawdown(config.auto_deleverage_drawdown_pct);
  }, [config]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(
        {
          ...config,
          max_daily_loss_pct: maxDailyLoss,
          max_weekly_loss_pct: maxWeeklyLoss,
          consecutive_loss_limit: consecutiveLossLimit,
          stop_loss_mode: stopLossMode,
          black_swan_threshold: blackSwanThreshold,
          auto_deleverage_drawdown_pct: autoDeleverageDrawdown,
        },
        'Risk defaults saved'
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <Panel title="Risk Defaults">
      <div className="space-y-4 max-w-lg">
        <SettingRow label={`Max Daily Loss: ${maxDailyLoss}%`}>
          <input type="range" min={1} max={20} value={maxDailyLoss} onChange={e => setMaxDailyLoss(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label={`Max Weekly Loss: ${maxWeeklyLoss}%`}>
          <input type="range" min={1} max={30} value={maxWeeklyLoss} onChange={e => setMaxWeeklyLoss(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label={`Consecutive Loss Limit: ${consecutiveLossLimit}`}>
          <input type="range" min={1} max={10} value={consecutiveLossLimit} onChange={e => setConsecutiveLossLimit(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label="Stop Loss Mode">
          <div className="flex gap-2">
            <button onClick={() => setStopLossMode('atr')} className={cn('px-3 py-1.5 rounded-md border text-xs', stopLossMode === 'atr' ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground')}>ATR Multiplier</button>
            <button onClick={() => setStopLossMode('fixed')} className={cn('px-3 py-1.5 rounded-md border text-xs', stopLossMode === 'fixed' ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground')}>Fixed %</button>
          </div>
        </SettingRow>
        <SettingRow label={`Black Swan Threshold: ${blackSwanThreshold}%`}>
          <input type="range" min={5} max={25} value={blackSwanThreshold} onChange={e => setBlackSwanThreshold(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>
        <SettingRow label={`Auto-Deleverage Drawdown: ${autoDeleverageDrawdown}%`}>
          <input type="range" min={5} max={30} value={autoDeleverageDrawdown} onChange={e => setAutoDeleverageDrawdown(Number(e.target.value))} className="w-full accent-accent" />
        </SettingRow>
        <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-4 py-2 rounded-md bg-accent text-primary-foreground text-xs font-semibold disabled:opacity-60">
          <Save className="h-3.5 w-3.5" /> {saving ? 'Saving…' : 'Save'}
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
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookPreview, setWebhookPreview] = useState('');
  const [webhookConfigured, setWebhookConfigured] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchNotificationRules()
      .then(setRules)
      .catch(() => {
        // Keep fallback defaults in local state if API is temporarily unavailable.
      });
    fetchDiscordWebhook()
      .then((data) => {
        setWebhookConfigured(data.configured);
        setWebhookPreview(data.webhook_url_preview || '');
      })
      .catch(() => {});
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
      await Promise.all([
        updateNotificationRules(normalized),
        webhookUrl.trim() ? updateDiscordWebhook(webhookUrl.trim()) : Promise.resolve(),
      ]);
      setRules(normalized);
      toast.success('Notification settings saved');
    } catch {
      toast.error('Failed to save notification rules');
    } finally {
      setSaving(false);
    }
  };

  const handleTestWebhook = async () => {
    setTesting(true);
    try {
      await testDiscordWebhook();
      toast.success('Test message sent to Discord');
    } catch {
      toast.error('Failed to send Discord test message');
    } finally {
      setTesting(false);
    }
  };

  return (
    <Panel title="Notification Settings">
      <div className="space-y-4 max-w-lg">
        <SettingRow label="Discord Webhook URL">
          <div className="space-y-2">
            <div className="flex gap-2">
              <input type="password" value={webhookUrl} onChange={e => setWebhookUrl(e.target.value)} placeholder={webhookConfigured ? webhookPreview || 'Configured webhook' : 'https://discord.com/api/webhooks/...'} className="flex-1 px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent" />
              <button onClick={handleTestWebhook} disabled={testing} className="px-3 py-1.5 rounded-md border border-border text-xs hover:bg-secondary/50 transition-colors flex items-center gap-1 disabled:opacity-60">
                <Send className="h-3 w-3" /> {testing ? '…' : 'Test'}
              </button>
            </div>
            {webhookConfigured && !webhookUrl && (
              <p className="text-[10px] text-muted-foreground">A webhook is already configured. Enter a new URL only if you want to replace it.</p>
            )}
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

function ExchangeTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
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

function SystemTab() {
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
