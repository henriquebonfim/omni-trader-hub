import { cn } from '@/core/utils';
import type { IndicatorCondition, Strategy, StrategyPerformanceEntry } from '@/domains/strategy/types';
import { EmptyState } from '@/shared/ui/molecules/EmptyState';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { Copy, Edit2, FlaskConical, Plus, Search, Target, Trash2, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const TA_CATEGORIES: Record<string, string[]> = {
  'Overlap Studies': ['BBANDS', 'DEMA', 'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MAMA', 'SMA', 'T3', 'TEMA', 'TRIMA', 'WMA'],
  'Momentum': ['ADX', 'ADXR', 'APO', 'AROON', 'CCI', 'CMO', 'DX', 'MACD', 'MFI', 'MOM', 'PPO', 'ROC', 'RSI', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR'],
  'Volume': ['AD', 'ADOSC', 'OBV'],
  'Volatility': ['ATR', 'NATR', 'TRANGE'],
  'Price Transform': ['AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE'],
  'Cycle': ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE'],
};

import { deleteStrategy, fetchStrategies, fetchStrategyPerformance, saveStrategy, updateStrategy } from '@/domains/strategy/api';

export default function StrategyLab() {
  const navigate = useNavigate();
  const [showEditor, setShowEditor] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [performance, setPerformance] = useState<StrategyPerformanceEntry[]>([]);

  const refetch = () => {
    fetchStrategies().then(res => { if (res.length > 0) setStrategies(res); }).catch(console.error);
    fetchStrategyPerformance().then(setPerformance).catch(console.error);
  };

  useEffect(() => { refetch(); }, []);

  const builtins = strategies.filter(s => s.builtin);
  const customs = strategies.filter(s => !s.builtin);
  const strategyLookup = new Map(strategies.map((strategy) => [strategy.name, strategy]));
  const comparisonRows = performance.length > 0
    ? performance.map((entry) => {
        const strategy = strategyLookup.get(entry.name);
        return {
          name: entry.name,
          regime_affinity: entry.regime,
          win_rate: entry.win_rate,
          sharpe: entry.sharpe,
          avg_trade: strategy?.avg_trade,
          active_bots: strategy?.active_bots ?? entry.sample_size,
        };
      })
    : [];

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
              <StrategyCard
                key={s.name}
                strategy={s}
                onEdit={() => { setEditingStrategy(s); setShowEditor(true); }}
                onDuplicate={() => saveStrategy({ ...s, name: `${s.name}_copy` }).then(() => refetch()).catch(console.error)}
                onDelete={() => deleteStrategy(s.name).then(() => refetch()).catch(console.error)}
                onBacktest={() => navigate(`/backtesting?strategy=${encodeURIComponent(s.name)}`)}
              />
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
              {comparisonRows.map(s => (
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
                  <td className="px-4 py-3 font-mono">{s.win_rate ?? '—'}{typeof s.win_rate === 'number' ? '%' : ''}</td>
                  <td className="px-4 py-3 font-mono">{typeof s.sharpe === 'number' ? s.sharpe.toFixed(2) : '—'}</td>
                  <td className="px-4 py-3 font-mono">{typeof s.avg_trade === 'number' ? `${s.avg_trade.toFixed(2)}%` : '—'}</td>
                  <td className="px-4 py-3 font-mono">{s.active_bots}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Strategy Editor Drawer */}
      {showEditor && <StrategyEditor strategy={editingStrategy} onClose={() => setShowEditor(false)} onSaved={() => { setShowEditor(false); refetch(); }} onBacktest={(name) => navigate(`/backtesting?strategy=${encodeURIComponent(name)}`)} />}
    </div>
  );
}

function StrategyCard({ strategy, onEdit, onDuplicate, onDelete, onBacktest, readonly }: { strategy: Strategy; onEdit: () => void; onDuplicate?: () => void; onDelete?: () => void; onBacktest?: () => void; readonly?: boolean }) {
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
          <button onClick={onDuplicate} className="px-2 py-1 rounded text-[11px] text-muted-foreground hover:bg-secondary transition-colors flex items-center gap-1">
            <Copy className="h-3 w-3" /> Duplicate
          </button>
          <button onClick={onBacktest} className="px-2 py-1 rounded text-[11px] text-accent hover:bg-accent/10 transition-colors flex items-center gap-1">
            <Target className="h-3 w-3" /> Backtest
          </button>
          <button onClick={onDelete} className="px-2 py-1 rounded text-[11px] text-danger hover:bg-danger/10 transition-colors flex items-center gap-1 ml-auto">
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
}

function StrategyEditor({ strategy, onClose, onSaved, onBacktest }: { strategy: Strategy | null; onClose: () => void; onSaved: () => void; onBacktest: (name: string) => void }) {
  const [name, setName] = useState(strategy?.name || '');
  const [description, setDescription] = useState(strategy?.description || '');
  const [regime, setRegime] = useState(strategy?.regime_affinity || 'all');
  const [indicatorSearch, setIndicatorSearch] = useState('');
  const [saving, setSaving] = useState(false);

  type ConditionType = 'entry_long' | 'entry_short' | 'exit_long' | 'exit_short';
  type ConditionRow = { id: string; indicator: string; conditionType: ConditionType; operator: IndicatorCondition['operator']; value: string };

  const toRows = (type: ConditionType, conds?: IndicatorCondition[]): ConditionRow[] =>
    (conds ?? []).map((c, i) => ({ id: `${type}-${i}`, indicator: c.indicator, conditionType: type, operator: c.operator, value: String(c.value) }));

  const [conditions, setConditions] = useState<ConditionRow[]>([
    ...toRows('entry_long', strategy?.entry_long),
    ...toRows('entry_short', strategy?.entry_short),
    ...toRows('exit_long', strategy?.exit_long),
    ...toRows('exit_short', strategy?.exit_short),
  ]);

  const addCondition = (indicator: string) => {
    setConditions(prev => [...prev, { id: `${Date.now()}`, indicator, conditionType: 'entry_long', operator: '>', value: '0' }]);
  };

  const updateCondition = (id: string, patch: Partial<ConditionRow>) => {
    setConditions(prev => prev.map(c => c.id === id ? { ...c, ...patch } : c));
  };

  const removeCondition = (id: string) => {
    setConditions(prev => prev.filter(c => c.id !== id));
  };

  const handleSave = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      const byType = (type: ConditionType): IndicatorCondition[] =>
        conditions
          .filter(c => c.conditionType === type)
          .map(c => ({ indicator: c.indicator, operator: c.operator, value: isNaN(Number(c.value)) ? c.value : Number(c.value) }));

      const payload: Partial<Strategy> = {
        name: name.trim(),
        description,
        regime_affinity: regime as Strategy['regime_affinity'],
        entry_long: byType('entry_long'),
        entry_short: byType('entry_short'),
        exit_long: byType('exit_long'),
        exit_short: byType('exit_short'),
      };
      if (strategy) {
        await updateStrategy(strategy.name, payload);
      } else {
        await saveStrategy(payload);
      }
      onSaved();
    } catch (e) {
      console.error('save strategy error', e);
    } finally {
      setSaving(false);
    }
  };

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
            <label className="text-[11px] text-muted-foreground mb-1 block">Indicators (TA-Lib) — click to add condition</label>
            <div className="relative mb-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
              <input
                value={indicatorSearch}
                onChange={e => setIndicatorSearch(e.target.value)}
                placeholder="Search indicators..."
                className="w-full pl-8 pr-3 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
              />
            </div>
            <div className="max-h-48 overflow-y-auto border border-border rounded-md">
              {Object.entries(filteredCategories).map(([cat, indicators]) => (
                <div key={cat}>
                  <div className="px-3 py-1.5 bg-secondary/50 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider sticky top-0">{cat}</div>
                  {indicators.map(ind => (
                    <button
                      key={ind}
                      onClick={() => addCondition(ind)}
                      className="w-full text-left px-3 py-1.5 text-xs hover:bg-accent/10 hover:text-accent transition-colors font-mono flex items-center justify-between group"
                    >
                      {ind}
                      <span className="text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">+ add</span>
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Conditions placeholder */}
          {/* Conditions Builder */}
          <div>
            <label className="text-[11px] text-muted-foreground mb-2 block">
              Conditions ({conditions.length}) — define entry/exit rules
            </label>
            {conditions.length === 0 ? (
              <div className="rounded-md border border-border/50 bg-secondary/10 p-3 text-center">
                <p className="text-[11px] text-muted-foreground">Click an indicator above to add a condition</p>
              </div>
            ) : (
              <div className="space-y-2">
                {conditions.map(cond => (
                  <div key={cond.id} className="flex items-center gap-1.5 rounded-md border border-border bg-secondary/20 p-2">
                    <span className="text-[11px] font-mono text-accent shrink-0 w-16 truncate">{cond.indicator}</span>
                    <select
                      value={cond.conditionType}
                      onChange={e => updateCondition(cond.id, { conditionType: e.target.value as ConditionType })}
                      className="flex-1 px-1.5 py-1 rounded border border-border bg-secondary/30 text-[11px] focus:outline-none focus:ring-1 focus:ring-accent"
                    >
                      <option value="entry_long">Entry Long</option>
                      <option value="entry_short">Entry Short</option>
                      <option value="exit_long">Exit Long</option>
                      <option value="exit_short">Exit Short</option>
                    </select>
                    <select
                      value={cond.operator}
                      onChange={e => updateCondition(cond.id, { operator: e.target.value as IndicatorCondition['operator'] })}
                      className="w-20 px-1.5 py-1 rounded border border-border bg-secondary/30 text-[11px] focus:outline-none focus:ring-1 focus:ring-accent"
                    >
                      <option value=">">{">"}</option>
                      <option value="<">{"<"}</option>
                      <option value=">=">{">="}</option>
                      <option value="<=">{"<="}</option>
                      <option value="crosses_above">↑ cross</option>
                      <option value="crosses_below">↓ cross</option>
                    </select>
                    <input
                      type="text"
                      value={cond.value}
                      onChange={e => updateCondition(cond.id, { value: e.target.value })}
                      className="w-14 px-1.5 py-1 rounded border border-border bg-secondary/30 text-[11px] font-mono focus:outline-none focus:ring-1 focus:ring-accent"
                      placeholder="value"
                    />
                    <button onClick={() => removeCondition(cond.id)} className="p-1 rounded hover:bg-danger/10 text-danger/70 hover:text-danger transition-colors">
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={!name.trim() || saving}
              className="flex-1 py-2.5 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60"
            >
              {saving ? 'Saving…' : 'Save Strategy'}
            </button>
            <button onClick={() => onBacktest(name.trim() || strategy?.name || 'ADX Trend')} className="px-4 py-2.5 rounded-md border border-border text-xs font-medium hover:bg-secondary/50 transition-colors">
              Backtest
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
