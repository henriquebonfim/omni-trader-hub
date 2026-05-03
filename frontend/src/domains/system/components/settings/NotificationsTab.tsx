import React, { useEffect, useState } from 'react';
import { Save, Send } from 'lucide-react';
import { toast } from 'sonner';
import { Panel } from '@/shared/ui/molecules/Panel';
import { cn } from '@/core/utils';
import {
  fetchDiscordWebhook,
  fetchNotificationRules,
  testDiscordWebhook,
  updateDiscordWebhook,
  updateNotificationRules,
} from '@/domains/system/api';
import type { AppConfig, NotificationRules } from '@/domains/system/types';
import { SettingRow } from './SettingRow';

export function NotificationsTab({ config }: { config: AppConfig }) {
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
