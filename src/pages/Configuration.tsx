import { Panel } from '@/components/shared/Panel';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { Loader2, Check } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

export default function Configuration() {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [strategies, setStrategies] = useState(['adx_trend', 'bollinger', 'breakout']);
  const allStrategies = [
    { id: 'adx_trend', label: 'ADX Trend' },
    { id: 'bollinger', label: 'Bollinger Bands' },
    { id: 'breakout', label: 'Breakout' },
    { id: 'ema_volume', label: 'EMA Volume' },
    { id: 'zscore', label: 'Z-Score' },
  ];

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => { setSaving(false); setSaved(true); setTimeout(() => setSaved(false), 2000); }, 1000);
  };

  const inputClass = "w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground";

  return (
    <div className="space-y-4 animate-slide-in max-w-3xl">
      <h1 className="text-lg font-bold text-foreground">⚙️ Configuration</h1>

      <Accordion type="multiple" defaultValue={['exchange', 'trading', 'risk', 'strategies', 'notifications']} className="space-y-2">
        <AccordionItem value="exchange" className="border border-border rounded-lg bg-card px-4">
          <AccordionTrigger className="text-sm font-semibold">Exchange Settings</AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-4">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">API Key</label>
                <input type="password" defaultValue="bfx_****" className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">API Secret</label>
                <input type="password" defaultValue="****" className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Subaccount</label>
                <input type="text" defaultValue="" placeholder="Optional" className={inputClass} />
              </div>
              <div className="flex items-end gap-3 pb-1">
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-border" />
                  Paper Mode
                </label>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="trading" className="border border-border rounded-lg bg-card px-4">
          <AccordionTrigger className="text-sm font-semibold">Trading Parameters</AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-4">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Symbol</label>
                <input type="text" defaultValue="BTC/USDT" className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Primary Timeframe</label>
                <select defaultValue="1h" className={inputClass}>
                  <option value="15m">15m</option><option value="1h">1h</option><option value="4h">4h</option><option value="1d">1d</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Leverage</label>
                <input type="number" defaultValue={3.0} step={0.5} className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Position Size (%)</label>
                <input type="number" defaultValue={2.0} step={0.1} className={inputClass} />
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="risk" className="border border-border rounded-lg bg-card px-4">
          <AccordionTrigger className="text-sm font-semibold">Risk Management</AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-4">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Max Daily Loss (%)</label>
                <input type="number" defaultValue={5.0} step={0.5} className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Max Positions</label>
                <input type="number" defaultValue={1} className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Stop Loss (%)</label>
                <input type="number" defaultValue={2.0} step={0.1} className={inputClass} />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Take Profit (%)</label>
                <input type="number" defaultValue={3.5} step={0.1} className={inputClass} />
              </div>
              <div className="flex items-end gap-3 pb-1">
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-border" />
                  Use ATR-based Stops
                </label>
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Trailing Stop Activation (%)</label>
                <input type="number" defaultValue={1.5} step={0.1} className={inputClass} />
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="strategies" className="border border-border rounded-lg bg-card px-4">
          <AccordionTrigger className="text-sm font-semibold">Strategy Selection</AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3 pb-4">
              <div className="flex gap-2 mb-2">
                <button onClick={() => setStrategies(allStrategies.map((s) => s.id))} className="text-xs text-primary hover:underline">Select All</button>
                <button onClick={() => setStrategies([])} className="text-xs text-muted-foreground hover:underline">Deselect All</button>
              </div>
              {allStrategies.map((s) => (
                <label key={s.id} className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                  <input
                    type="checkbox"
                    checked={strategies.includes(s.id)}
                    onChange={(e) => setStrategies(e.target.checked ? [...strategies, s.id] : strategies.filter((x) => x !== s.id))}
                    className="rounded border-border"
                  />
                  {s.label}
                </label>
              ))}
              {strategies.length === 0 && (
                <p className="text-xs text-trading-red">⚠️ No strategies selected. Bot will not trade.</p>
              )}
              <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer mt-3">
                <input type="checkbox" defaultChecked className="rounded border-border" />
                Enable Regime Filter
              </label>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="notifications" className="border border-border rounded-lg bg-card px-4">
          <AccordionTrigger className="text-sm font-semibold">Notifications</AccordionTrigger>
          <AccordionContent>
            <div className="space-y-3 pb-4">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Discord Webhook URL</label>
                <input type="password" defaultValue="https://discord.com/api/webhooks/****" className={inputClass} />
              </div>
              <Button variant="outline" size="sm" className="text-xs">Test Webhook</Button>
              <div className="space-y-2 mt-3">
                {['Trade executions', 'Circuit breaker triggers', 'Daily summaries', 'Errors/warnings'].map((n) => (
                  <label key={n} className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded border-border" />
                    {n}
                  </label>
                ))}
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <div className="flex gap-3">
        <Button onClick={handleSave} disabled={saving} className="bg-primary text-primary-foreground hover:bg-primary/90">
          {saving ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Saving...</> : saved ? <><Check className="h-4 w-4 mr-2" /> Saved!</> : 'Save Configuration'}
        </Button>
        <Button variant="outline">Reload from Server</Button>
        <Button variant="outline" className="border-trading-red/30 text-trading-red hover:bg-trading-red/10">Reset Defaults</Button>
      </div>
    </div>
  );
}
