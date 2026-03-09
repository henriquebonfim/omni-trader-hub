import { useState } from 'react';
import { Panel } from '@/components/shared/Panel';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { EmptyState } from '@/components/shared/EmptyState';
import { mockStrategies } from '@/lib/mock-data';
import { cn } from '@/lib/utils';
import { Plus, FlaskConical, Edit2, Copy, Target, Trash2, X, Search } from 'lucide-react';
import type { Strategy } from '@/types';

const TA_CATEGORIES: Record<string, string[]> = {
  'Overlap Studies': ['BBANDS', 'DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MAMA', 'SMA', 'T3', 'TEMA', 'TRIMA', 'WMA'],
  'Momentum': ['ADX', 'ADXR', 'APO', 'AROON', 'CCI', 'CMO', 'DX', 'MACD', 'MFI', 'MOM', 'PPO', 'ROC', 'RSI', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR'],
  'Volume': ['AD', 'ADOSC', 'OBV'],
  'Volatility': ['ATR', 'NATR', 'TRANGE'],
  'Price Transform': ['AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE'],
  'Cycle': ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE'],
};

export default function StrategyLab() {
  const [showEditor, setShowEditor] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);

  const builtins = mockStrategies.filter(s => s.builtin);
  const customs = mockStrategies.filter(s => !s.builtin);

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Strategy Lab</h1>
          <p className="text-xs text-muted-foreground">Browse, create, and compare trading strategies</p>
        </div>
        <button
          onClick={() => { setEditingStrategy(null); setShowEditor(true); }}
          className="flex items-center gap-2 px-3 py-2 rounded-md bg-accent text-primary-foreground text-xs font-medium hover:bg-accent/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" /> New Strategy
        </button>
      </div>

      {/* Built-in Strategies */}
      <Panel title="Built-in Strategies" subtitle="Core strategies — read only">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {builtins.map(s => (
            <StrategyCard key={s.name} strategy={s} onEdit={() => {}} readonly />
          ))}
        </div>
      </Panel>

      {/* Custom Strategies */}
      <Panel title="Custom Strategies" subtitle="Your created strategies">
        {customs.length === 0 ? (
          <EmptyState
            icon={FlaskConical}
            title="No custom strategies yet"
            description="Create your first custom strategy using any TA-Lib indicator"
            action={
              <button
                onClick={() => setShowEditor(true)}
                className="px-3 py-2 rounded-md bg-accent text-primary-foreground text-xs font-medium"
              >
                Create Strategy
              </button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {customs.map(s => (
              <StrategyCard key={s.name} strategy={s} onEdit={() => { setEditingStrategy(s); setShowEditor(true); }} />
            ))}
          </div>
        )}
      </Panel>

      {/* Performance Comparison */}
      <Panel title="Strategy Performance Comparison" noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {['Strategy', 'Regime', 'Win Rate', 'Sharpe', 'Avg Trade', 'Active Bots'].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-medium text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {mockStrategies.map(s => (
                <tr key={s.name} className="border-b border-border/50 hover:bg-secondary/30">
                  <td className="px-4 py-3 font-medium">{s.name}</td>
                  <td className="px-4 py-3">
                    <StatusBadge
                      variant={s.regime_affinity === 'trending' ? 'success' : s.regime_affinity === 'ranging' ? 'info' : 'warning'}
                      size="sm"
                    >
                      {s.regime_affinity.toUpperCase()}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3 font-mono">{s.win_rate}%</td>
                  <td className="px-4 py-3 font-mono">{s.sharpe?.toFixed(2)}</td>
                  <td className="px-4 py-3 font-mono">{s.avg_trade?.toFixed(2)}%</td>
                  <td className="px-4 py-3 font-mono">{s.active_bots}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Strategy Editor Drawer */}
      {showEditor && <StrategyEditor strategy={editingStrategy} onClose={() => setShowEditor(false)} />}
    </div>
  );
}

function StrategyCard({ strategy, onEdit, readonly }: { strategy: Strategy; onEdit: () => void; readonly?: boolean }) {
  return (
    <div className="rounded-lg border border-border bg-secondary/20 p-4 hover:bg-secondary/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">{strategy.name}</h4>
        <StatusBadge
          variant={strategy.regime_affinity === 'trending' ? 'success' : strategy.regime_affinity === 'ranging' ? 'info' : 'warning'}
          size="sm"
        >
          {strategy.regime_affinity.toUpperCase()}
        </StatusBadge>
      </div>
      <p className="text-[11px] text-muted-foreground mb-3 line-clamp-2">{strategy.description}</p>

      <div className="grid grid-cols-3 gap-2 text-[11px] mb-3">
        <div>
          <span className="text-muted-foreground">Win Rate</span>
          <p className="font-mono font-medium">{strategy.win_rate || '—'}%</p>
        </div>
        <div>
          <span className="text-muted-foreground">Sharpe</span>
          <p className="font-mono font-medium">{strategy.sharpe?.toFixed(2) || '—'}</p>
        </div>
        <div>
          <span className="text-muted-foreground">Bots</span>
          <p className="font-mono font-medium">{strategy.active_bots || 0}</p>
        </div>
      </div>

      {!readonly && (
        <div className="flex gap-1.5 pt-2 border-t border-border/50">
          <button onClick={onEdit} className="px-2 py-1 rounded text-[11px] text-accent hover:bg-accent/10 transition-colors flex items-center gap-1">
            <Edit2 className="h-3 w-3" /> Edit
          </button>
          <button className="px-2 py-1 rounded text-[11px] text-muted-foreground hover:bg-secondary transition-colors flex items-center gap-1">
            <Copy className="h-3 w-3" /> Duplicate
          </button>
          <button className="px-2 py-1 rounded text-[11px] text-accent hover:bg-accent/10 transition-colors flex items-center gap-1">
            <Target className="h-3 w-3" /> Backtest
          </button>
          <button className="px-2 py-1 rounded text-[11px] text-danger hover:bg-danger/10 transition-colors flex items-center gap-1 ml-auto">
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
}

function StrategyEditor({ strategy, onClose }: { strategy: Strategy | null; onClose: () => void }) {
  const [name, setName] = useState(strategy?.name || '');
  const [description, setDescription] = useState(strategy?.description || '');
  const [regime, setRegime] = useState(strategy?.regime_affinity || 'all');
  const [indicatorSearch, setIndicatorSearch] = useState('');

  const filteredCategories = Object.entries(TA_CATEGORIES).reduce((acc, [cat, indicators]) => {
    const filtered = indicators.filter(i => i.toLowerCase().includes(indicatorSearch.toLowerCase()));
    if (filtered.length > 0) acc[cat] = filtered;
    return acc;
  }, {} as Record<string, string[]>);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-card border-l border-border h-full overflow-y-auto animate-fade-in">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-sm font-semibold">{strategy ? 'Edit Strategy' : 'New Custom Strategy'}</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-secondary transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Strategy Name</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="My Strategy" className="w-full px-3 py-2 rounded-md border border-border bg-secondary/30 text-sm focus:outline-none focus:ring-1 focus:ring-accent" />
          </div>

          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Description</label>
            <textarea value={description} onChange={e => setDescription(e.target.value)} rows={2} placeholder="Describe your strategy..." className="w-full px-3 py-2 rounded-md border border-border bg-secondary/30 text-sm focus:outline-none focus:ring-1 focus:ring-accent resize-none" />
          </div>

          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Regime Affinity</label>
            <div className="flex gap-2">
              {(['trending', 'ranging', 'volatile', 'all'] as const).map(r => (
                <button key={r} onClick={() => setRegime(r)} className={cn(
                  'px-3 py-1.5 rounded-md border text-xs capitalize transition-colors',
                  regime === r ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground'
                )}>
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Indicator Selector */}
          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Indicators (TA-Lib)</label>
            <div className="relative mb-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
              <input
                value={indicatorSearch}
                onChange={e => setIndicatorSearch(e.target.value)}
                placeholder="Search indicators..."
                className="w-full pl-8 pr-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
              />
            </div>
            <div className="max-h-60 overflow-y-auto border border-border rounded-md">
              {Object.entries(filteredCategories).map(([cat, indicators]) => (
                <div key={cat}>
                  <div className="px-3 py-1.5 bg-secondary/50 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider sticky top-0">{cat}</div>
                  {indicators.map(ind => (
                    <button key={ind} className="w-full text-left px-3 py-1.5 text-xs hover:bg-secondary/30 transition-colors font-mono">
                      {ind}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Conditions placeholder */}
          <div className="rounded-md border border-border/50 bg-secondary/10 p-3">
            <p className="text-[11px] text-muted-foreground text-center">Select indicators above to build entry/exit conditions</p>
          </div>

          <div className="flex gap-2">
            <button className="flex-1 py-2.5 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors">
              Save Strategy
            </button>
            <button className="px-4 py-2.5 rounded-md border border-border text-xs font-medium hover:bg-secondary/50 transition-colors">
              Backtest
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
