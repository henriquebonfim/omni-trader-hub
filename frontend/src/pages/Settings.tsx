import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import {
  fetchConfig,
  fetchEnvVars,
  restartSystem,
  updateConfig,
} from '@/domains/system/api';
import type { AppConfig, EnvVariable } from '@/domains/system/types';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

import { GeneralTab } from '@/domains/system/components/settings/GeneralTab';
import { EnvironmentTab } from '@/domains/system/components/settings/EnvironmentTab';
import { RiskTab } from '@/domains/system/components/settings/RiskTab';
import { NotificationsTab } from '@/domains/system/components/settings/NotificationsTab';
import { ExchangeTab } from '@/domains/system/components/settings/ExchangeTab';
import { SystemTab } from '@/domains/system/components/settings/SystemTab';

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

      <div className="mt-4">
        {tab === 'general' && <GeneralTab config={config} onSave={handleSaveConfig} />}
        {tab === 'environment' && <EnvironmentTab envVars={envVars} onRestart={handleRestartServices} />}
        {tab === 'risk' && <RiskTab config={config} onSave={handleSaveConfig} />}
        {tab === 'notifications' && <NotificationsTab config={config} />}
        {tab === 'exchange' && <ExchangeTab config={config} onSave={handleSaveConfig} />}
        {tab === 'system' && <SystemTab />}
      </div>
    </div>
  );
}
