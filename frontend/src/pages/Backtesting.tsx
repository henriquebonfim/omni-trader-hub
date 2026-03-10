import { useState } from 'react';
import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { mockStrategies } from '@/domains/strategy/mocks';
import { mockBacktestResults } from '@/domains/trade/mocks';
import { mockMarkets } from '@/domains/market/mocks';
import { cn } from '@/core/utils';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Play, Download } from 'lucide-react';

const metricTargets: Record<string, { target: number; better: 'higher' | 'lower' }> = {
  sharpe_ratio: { target: 1.0, better: 'higher' },
  sortino_ratio: { target: 1.5, better: 'higher' },
  max_drawdown_pct: { target: 15, better: 'lower' },
  profit_factor: { target: 1.5, better: 'higher' },
  win_rate_pct: { target: 45, better: 'higher' },
};

export default function Backtesting() {
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [strategy, setStrategy] = useState('ADX Trend');
  const [timeframe, setTimeframe] = useState('1h');
  const [running, setRunning] = useState(false);
  const [hasResults, setHasResults] = useState(true);
  const r = mockBacktestResults;

  const handleRun = () => {
    setRunning(true);
    setTimeout(() => { setRunning(false); setHasResults(true); }, 2000);
  };

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Backtesting</h1>

      {/* Config */}
      <Panel title="Backtest Configuration">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Symbol</label>
            <select value={symbol} onChange={e => setSymbol(e.target.value)} className="w-full px-2 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
              {mockMarkets.map(m => <option key={m.symbol} value={m.symbol}>{m.symbol}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Strategy</label>
            <select value={strategy} onChange={e => setStrategy(e.target.value)} className="w-full px-2 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
              {mockStrategies.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[11px] text-muted-foreground mb-1 block">Timeframe</label>
            <select value={timeframe} onChange={e => setTimeframe(e.target.value)} className="w-full px-2 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
              {['5m', '15m', '1h', '4h', '1d'].map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleRun}
              disabled={running}
              className={cn(
                'w-full flex items-center justify-center gap-2 py-2 rounded-md text-xs font-semibold transition-colors',
                running ? 'bg-accent/50 text-accent-foreground cursor-not-allowed' : 'bg-accent text-primary-foreground hover:bg-accent/90'
              )}
            >
              {running ? (
                <><span className="animate-spin h-3 w-3 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full" /> Running...</>
              ) : (
                <><Play className="h-3.5 w-3.5" /> Run Backtest</>
              )}
            </button>
          </div>
        </div>

        {/* Presets */}
        <div className="flex gap-2 mt-3">
          {['Bear Market 2022', 'Bull Run 2024', 'Last 6 Months'].map(p => (
            <button key={p} className="px-2.5 py-1 rounded-md border border-border text-[11px] text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors">
              {p}
            </button>
          ))}
        </div>
      </Panel>

      {hasResults && (
        <>
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            {[
              { label: 'Total PnL', value: `$${r.total_pnl.toFixed(2)}`, color: r.total_pnl >= 0 ? 'text-success' : 'text-danger' },
              { label: 'Return', value: `${r.total_return_pct.toFixed(2)}%`, color: 'text-success' },
              { label: 'Sharpe', value: r.sharpe_ratio.toFixed(2), pass: r.sharpe_ratio >= 1.0 },
              { label: 'Sortino', value: r.sortino_ratio.toFixed(2), pass: r.sortino_ratio >= 1.5 },
              { label: 'Max DD', value: `${r.max_drawdown_pct.toFixed(1)}%`, pass: r.max_drawdown_pct <= 15 },
              { label: 'Win Rate', value: `${r.win_rate_pct.toFixed(1)}%`, pass: r.win_rate_pct >= 45 },
              { label: 'Profit Factor', value: r.profit_factor.toFixed(2), pass: r.profit_factor >= 1.5 },
            ].map(m => (
              <div key={m.label} className="rounded-lg border border-border bg-card p-3">
                <p className="text-[10px] text-muted-foreground mb-0.5">{m.label}</p>
                <div className="flex items-center gap-1.5">
                  <span className={cn('text-sm font-semibold font-mono', m.color || 'text-foreground')}>{m.value}</span>
                  {m.pass !== undefined && (
                    <span className="text-[10px]">{m.pass ? '✅' : '❌'}</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Extra metrics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { label: 'Total Trades', value: r.total_trades },
              { label: 'Wins / Losses', value: `${r.wins} / ${r.losses}` },
              { label: 'Avg Win/Loss', value: r.avg_win_loss_ratio.toFixed(2) },
              { label: 'Best Trade', value: `$${r.best_trade_pnl.toFixed(2)}` },
              { label: 'Worst Trade', value: `$${r.worst_trade_pnl.toFixed(2)}` },
            ].map(m => (
              <div key={m.label} className="rounded-lg border border-border bg-card p-3">
                <p className="text-[10px] text-muted-foreground mb-0.5">{m.label}</p>
                <span className="text-sm font-semibold font-mono">{m.value}</span>
              </div>
            ))}
          </div>

          {/* Equity Chart */}
          <Panel title="Equity Curve" actions={<button className="text-[11px] text-accent flex items-center gap-1"><Download className="h-3 w-3" /> Export</button>}>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={r.equity_curve}>
                  <defs>
                    <linearGradient id="btGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(212 100% 67%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(212 100% 67%)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(3 90% 63%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(3 90% 63%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" tick={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `$${(v/1000).toFixed(1)}k`} />
                  <Tooltip contentStyle={{ background: 'hsl(216 18% 11%)', border: '1px solid hsl(215 10% 22%)', borderRadius: 8, fontSize: 12 }} labelFormatter={() => ''} />
                  <Area type="monotone" dataKey="equity" stroke="hsl(212 100% 67%)" fill="url(#btGrad)" strokeWidth={2} />
                  <Area type="monotone" dataKey="drawdown" stroke="hsl(3 90% 63%)" fill="url(#ddGrad)" strokeWidth={1} yAxisId="right" />
                  <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10, fill: '#8b949e' }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `${v.toFixed(0)}%`} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Panel>

          {/* Monthly Returns */}
          <Panel title="Monthly Returns">
            <div className="grid grid-cols-6 gap-2">
              {r.monthly_returns.map((m, i) => (
                <div
                  key={i}
                  className={cn(
                    'rounded p-2 text-center text-xs font-mono',
                    m.return_pct >= 0 ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
                  )}
                >
                  <p className="text-[10px] text-muted-foreground">{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m.month - 1]}</p>
                  <p className="font-medium">{m.return_pct >= 0 ? '+' : ''}{m.return_pct}%</p>
                </div>
              ))}
            </div>
          </Panel>
        </>
      )}
    </div>
  );
}
