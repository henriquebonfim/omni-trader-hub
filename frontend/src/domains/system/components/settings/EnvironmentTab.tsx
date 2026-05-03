import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { AlertTriangle, Eye, EyeOff, RotateCcw, Save } from 'lucide-react';
import { Panel } from '@/shared/ui/molecules/Panel';
import { updateEnvVars } from '@/domains/system/api';
import type { EnvVariable } from '@/domains/system/types';

export function EnvironmentTab({ envVars, onRestart }: { envVars: EnvVariable[]; onRestart: () => Promise<void> }) {
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
