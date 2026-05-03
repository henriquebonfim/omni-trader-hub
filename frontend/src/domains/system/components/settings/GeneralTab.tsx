import { cn } from '@/core/utils';
import { Panel } from '@/shared/ui/molecules/Panel';
import type { AppConfig } from '@/domains/system/types';
import { Save } from 'lucide-react';
import { useEffect, useState } from 'react';
import { SettingRow } from './SettingRow';

export function GeneralTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
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
