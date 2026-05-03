import React, { useEffect, useState } from 'react';
import { Save } from 'lucide-react';
import { Panel } from '@/shared/ui/molecules/Panel';
import { cn } from '@/core/utils';
import type { AppConfig } from '@/domains/system/types';
import { SettingRow } from './SettingRow';

export function RiskTab({ config, onSave }: { config: AppConfig; onSave: (config: AppConfig, successMessage?: string) => Promise<void> }) {
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
