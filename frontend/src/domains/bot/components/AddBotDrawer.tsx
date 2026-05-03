import { cn } from '@/core/utils';
import { createBot } from '@/domains/bot/api';
import { fetchMarkets } from '@/domains/market/api';
import type { MarketPair } from '@/domains/market/types';
import { X } from 'lucide-react';
import { useEffect, useState } from 'react';

interface AddBotDrawerProps {
  onClose: () => void;
  onCreated: () => void;
}

export function AddBotDrawer({ onClose, onCreated }: AddBotDrawerProps) {
  const [symbol, setSymbol] = useState('');
  const [mode, setMode] = useState<'auto' | 'manual'>('auto');
  const [leverage, setLeverage] = useState(3);
  const [allocation, setAllocation] = useState(10);
  const [marketSearch, setMarketSearch] = useState('');
  const [markets, setMarkets] = useState<MarketPair[]>([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchMarkets().then(setMarkets).catch(console.error);
  }, []);

  const filteredMarkets = markets.filter(m =>
    m.symbol.toLowerCase().includes(marketSearch.toLowerCase())
  );

  const handleCreate = async () => {
    if (!symbol) return;
    setCreating(true);
    try {
      await createBot({ symbol, mode, leverage, balance_allocated: allocation });
      onCreated();
      onClose();
    } catch (e) {
      console.error('createBot error', e);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-card border-l border-border h-full overflow-y-auto animate-fade-in">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Add New Bot</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-secondary transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Symbol */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Symbol</label>
            <input
              placeholder="Search markets..."
              value={marketSearch}
              onChange={e => setMarketSearch(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-border bg-secondary/30 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent mb-2"
            />
            <div className="max-h-40 overflow-y-auto border border-border rounded-md">
              {filteredMarkets.map(m => (
                <button
                  key={m.symbol}
                  onClick={() => { setSymbol(m.symbol); setMarketSearch(m.symbol); }}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 text-xs hover:bg-secondary/50 transition-colors',
                    symbol === m.symbol && 'bg-accent/10 text-accent'
                  )}
                >
                  <span className="font-medium">{m.symbol}</span>
                  <span className="text-muted-foreground font-mono">${m.last_price.toLocaleString()}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Mode */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Mode</label>
            <div className="flex gap-2">
              {(['auto', 'manual'] as const).map(m => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={cn(
                    'flex-1 py-2 rounded-md border text-xs font-medium transition-colors',
                    mode === m ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground hover:text-foreground'
                  )}
                >
                  {m === 'auto' ? 'Auto (bot selects)' : 'Manual (lock strategy)'}
                </button>
              ))}
            </div>
          </div>

          {/* Leverage */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Leverage: {leverage}×</label>
            <input type="range" min={1} max={10} value={leverage} onChange={e => setLeverage(Number(e.target.value))}
              className="w-full accent-accent" />
          </div>

          {/* Allocation */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Allocation: {allocation}%</label>
            <input type="range" min={1} max={50} value={allocation} onChange={e => setAllocation(Number(e.target.value))}
              className="w-full accent-accent" />
          </div>

          <button
            onClick={handleCreate}
            disabled={!symbol || creating}
            className="w-full py-2.5 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60"
          >
            {creating ? 'Creating…' : 'Create Bot'}
          </button>
        </div>
      </div>
    </div>
  );
}
