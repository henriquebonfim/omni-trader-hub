import { Panel } from '@/components/shared/Panel';
import { StatCard } from '@/components/shared/StatCard';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { mockBacktestResults, mockMonthlyReturns, mockWalkForwardWindows, mockBootstrapCIs, mockEquityData } from '@/lib/mock-data';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { Loader2 } from 'lucide-react';

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export default function Backtesting() {
  const [running, setRunning] = useState(false);
  const [hasResults, setHasResults] = useState(true);
  const [config, setConfig] = useState({
    start_date: '2024-01-01',
    end_date: '2025-03-09',
    strategy: 'adx_trend',
    timeframe: '1h',
    initial_capital: 10000,
    position_size_pct: 2.0,
    leverage: 3.0,
  });

  const handleRun = () => {
    setRunning(true);
    setTimeout(() => { setRunning(false); setHasResults(true); }, 2000);
  };

  const r = mockBacktestResults;
  const meetsTarget = (metric: string, value: number) => {
    const targets: Record<string, (v: number) => boolean> = {
      sharpe_ratio: (v) => v > 1.0,
      max_drawdown_pct: (v) => v < 15,
      profit_factor: (v) => v > 1.5,
      win_rate_pct: (v) => v > 45,
    };
    return targets[metric]?.(value) ?? true;
  };

  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">🎯 Backtesting</h1>

      {/* Config Form */}
      <Panel title="Backtest Configuration">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Start Date</label>
            <input type="date" value={config.start_date} onChange={(e) => setConfig({ ...config, start_date: e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">End Date</label>
            <input type="date" value={config.end_date} onChange={(e) => setConfig({ ...config, end_date: e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Strategy</label>
            <select value={config.strategy} onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground">
              <option value="adx_trend">ADX Trend</option>
              <option value="bollinger">Bollinger Bands</option>
              <option value="breakout">Breakout</option>
              <option value="ema_volume">EMA Volume</option>
              <option value="zscore">Z-Score</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Timeframe</label>
            <div className="flex gap-1">
              {['15m', '1h', '4h', '1d'].map((tf) => (
                <button key={tf} onClick={() => setConfig({ ...config, timeframe: tf })}
                  className={`flex-1 px-2 py-2 text-xs rounded-md border ${config.timeframe === tf ? 'bg-primary text-primary-foreground border-primary' : 'bg-muted border-border text-muted-foreground'}`}>
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Initial Capital ($)</label>
            <input type="number" value={config.initial_capital} onChange={(e) => setConfig({ ...config, initial_capital: +e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Position Size (%)</label>
            <input type="number" step="0.1" value={config.position_size_pct} onChange={(e) => setConfig({ ...config, position_size_pct: +e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-muted-foreground">Leverage</label>
            <input type="number" step="0.5" value={config.leverage} onChange={(e) => setConfig({ ...config, leverage: +e.target.value })}
              className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
          </div>
          <div className="flex items-end">
            <Button onClick={handleRun} disabled={running} className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
              {running ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Running...</> : 'Run Backtest'}
            </Button>
          </div>
        </div>
      </Panel>

      {hasResults && (
        <>
          {/* Metrics Grid */}
          <Panel title="Performance Metrics">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {[
                { label: 'Total P&L', value: `$${r.total_pnl.toFixed(2)}`, variant: r.total_pnl >= 0 ? 'green' as const : 'red' as const },
                { label: 'Return', value: `${r.total_return_pct.toFixed(1)}%`, variant: 'green' as const },
                { label: 'Sharpe', value: r.sharpe_ratio.toFixed(2), variant: 'accent' as const, target: meetsTarget('sharpe_ratio', r.sharpe_ratio) },
                { label: 'Sortino', value: r.sortino_ratio.toFixed(2), variant: 'accent' as const },
                { label: 'Max DD', value: `${r.max_drawdown_pct.toFixed(1)}%`, variant: 'red' as const, target: meetsTarget('max_drawdown_pct', r.max_drawdown_pct) },
                { label: 'Profit Factor', value: r.profit_factor.toFixed(2), variant: 'accent' as const, target: meetsTarget('profit_factor', r.profit_factor) },
                { label: 'Win Rate', value: `${r.win_rate_pct.toFixed(1)}%`, variant: 'green' as const, target: meetsTarget('win_rate_pct', r.win_rate_pct) },
                { label: 'Avg W/L', value: r.avg_win_loss_ratio.toFixed(2), variant: 'accent' as const },
                { label: 'Total Trades', value: r.total_trades, variant: 'default' as const },
                { label: 'Best Trade', value: `$${r.best_trade_pnl.toFixed(2)}`, variant: 'green' as const },
              ].map((m) => (
                <div key={m.label} className="relative">
                  <StatCard label={m.label} value={m.value} variant={m.variant} />
                  {'target' in m && (
                    <span className="absolute top-2 right-2 text-xs">{m.target ? '✅' : '❌'}</span>
                  )}
                </div>
              ))}
            </div>
          </Panel>

          {/* Equity Chart */}
          <Panel title="Equity Curve">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockEquityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(215, 14%, 18%)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(215, 10%, 55%)' }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: 'hsl(215, 10%, 55%)' }} tickLine={false} axisLine={false} width={60} />
                  <Tooltip contentStyle={{ background: 'hsl(215, 25%, 11%)', border: '1px solid hsl(215, 14%, 22%)', borderRadius: 8, fontSize: 12 }} />
                  <Area type="monotone" dataKey="balance" stroke="hsl(140, 60%, 52%)" fill="hsl(140, 60%, 52%)" fillOpacity={0.1} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Panel>

          {/* Monthly Returns Heatmap */}
          <Panel title="Monthly Returns Heatmap">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr>
                    <th className="text-left py-2 text-muted-foreground">Year</th>
                    {months.map((m) => <th key={m} className="text-center py-2 text-muted-foreground">{m}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {[2024, 2025].map((year) => (
                    <tr key={year}>
                      <td className="py-1 text-foreground font-mono">{year}</td>
                      {Array.from({ length: 12 }, (_, i) => {
                        const entry = mockMonthlyReturns.find((r) => r.year === year && r.month === i + 1);
                        if (!entry) return <td key={i} className="text-center py-1"><span className="inline-block w-10 h-8 rounded bg-muted" /></td>;
                        const intensity = Math.min(1, Math.abs(entry.return_pct) / 10);
                        const bg = entry.return_pct >= 0
                          ? `rgba(63, 185, 80, ${0.15 + intensity * 0.6})`
                          : `rgba(248, 81, 73, ${0.15 + intensity * 0.6})`;
                        return (
                          <td key={i} className="text-center py-1">
                            <span className="inline-flex items-center justify-center w-10 h-8 rounded text-foreground font-mono" style={{ background: bg }}>
                              {entry.return_pct > 0 ? '+' : ''}{entry.return_pct.toFixed(1)}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Walk-Forward */}
            <Panel title="Walk-Forward Analysis">
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-muted-foreground">
                      <th className="text-left py-2">Window</th>
                      <th className="text-right py-2">In-Sample</th>
                      <th className="text-right py-2">Out-Sample</th>
                      <th className="text-right py-2">Degrad.</th>
                      <th className="text-center py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockWalkForwardWindows.map((w, i) => (
                      <tr key={i} className="border-t border-border">
                        <td className="py-2 text-muted-foreground">{w.test_start} → {w.test_end}</td>
                        <td className="py-2 text-right text-foreground font-mono">{w.in_sample_sharpe.toFixed(2)}</td>
                        <td className="py-2 text-right text-foreground font-mono">{w.out_sample_sharpe.toFixed(2)}</td>
                        <td className={`py-2 text-right font-mono ${Math.abs(w.degradation_pct) > 15 ? 'text-trading-red' : 'text-trading-green'}`}>
                          {w.degradation_pct.toFixed(1)}%
                        </td>
                        <td className="py-2 text-center">{Math.abs(w.degradation_pct) <= 15 ? '✅' : '⚠️'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>

            {/* Bootstrap CIs */}
            <Panel title="Bootstrap Confidence Intervals">
              <div className="space-y-3">
                {mockBootstrapCIs.map((ci) => (
                  <div key={ci.metric} className="p-3 rounded-lg bg-muted">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-foreground font-medium">{ci.metric}</span>
                      <span className="text-xs">{ci.excludes_zero ? '✅' : '❌'}</span>
                    </div>
                    <p className="text-lg font-bold text-foreground font-mono">
                      {ci.point_estimate.toFixed(2)}{' '}
                      <span className="text-xs text-muted-foreground font-normal">
                        [95% CI: {ci.ci_lower.toFixed(2)} – {ci.ci_upper.toFixed(2)}]
                      </span>
                    </p>
                  </div>
                ))}
                <p className="text-xs text-trading-green">✅ All CIs exclude zero expectancy</p>
              </div>
            </Panel>
          </div>
        </>
      )}
    </div>
  );
}
