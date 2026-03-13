import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { fetchBots, startBot, stopBot } from '@/domains/bot/api';
import { fetchSentiment } from '@/domains/market/api';
import { fetchEquitySnapshots, fetchTradeHistory } from '@/domains/trade/api';
import type { EquitySnapshot, Trade } from '@/domains/trade/types';
import { Panel } from '@/shared/components/Panel';
import { StatCard } from '@/shared/components/StatCard';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { ArrowRight, ArrowUpDown, Pause, Play, Square, TrendingUp, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const regimeIcons: Record<string, React.ReactNode> = {
  trending: <TrendingUp className="h-3 w-3" />,
  ranging: <ArrowUpDown className="h-3 w-3" />,
  volatile: <Zap className="h-3 w-3" />,
};

const regimeColors: Record<string, string> = {
  trending: 'success',
  ranging: 'info',
  volatile: 'warning',
};

export default function Dashboard() {
  const storeBots = useAppStore(s => s.bots);
  const setBots = useAppStore(s => s.setBots);
  const prices = useAppStore(s => s.livePrices);
  const bots = storeBots;
  const liveAlerts = useAppStore(s => s.alerts);
  const alerts = liveAlerts;

  const [trades, setTrades] = useState<Trade[]>([]);
  const [equityDataAll, setEquityDataAll] = useState<EquitySnapshot[]>([]);
  const [sentimentScore, setSentimentScore] = useState<number>(0);

  const refreshBots = () => fetchBots().then(setBots).catch(console.error);

  useEffect(() => {
    fetchBots().then(setBots).catch(console.error);
    fetchTradeHistory().then(res => setTrades(res.trades.slice(0, 10))).catch(console.error);
    fetchEquitySnapshots().then(setEquityDataAll).catch(console.error);
    fetchSentiment('BTC/USDT').then((res) => setSentimentScore(res.score)).catch(console.error);
  }, [setBots]);

  const activeBots = bots.filter(b => b.status === 'running');
  const totalValue = bots.reduce((s, b) => s + b.balance_allocated, 0);
  const totalPnl = activeBots.reduce((s, b) => s + b.daily_pnl, 0);
  const totalPnlPct = totalValue > 0 ? (totalPnl / totalValue) * 100 : 0;
  const openPositions = bots.filter(b => b.position).length;

  const [equityRange, setEquityRange] = useState<'7D' | '30D' | '90D'>('30D');
  let equityData = equityDataAll.slice(equityRange === '7D' ? -7 : equityRange === '30D' ? -30 : 0);
  if (equityData.length === 0) equityData = [{timestamp: Date.now(), equity: 0}];
  const hasCriticalAlert = alerts.some((a) => a.level === 'critical');
  const hasWarningAlert = alerts.some((a) => a.level === 'warning');
  const circuitBreakerLabel = alerts.length === 0 ? 'No alerts' : hasCriticalAlert ? 'Tripped' : hasWarningAlert ? 'Warning' : 'All OK';
  const circuitBreakerColor = alerts.length === 0 ? 'accent' : hasCriticalAlert ? 'red' : hasWarningAlert ? 'yellow' : 'green';

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Global Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard label="Portfolio Value" value={`$${totalValue.toLocaleString()}`} />
        <StatCard label="Today's PnL" value={`$${totalPnl.toFixed(2)}`} suffix={` (${totalPnlPct.toFixed(2)}%)`} color={totalPnl >= 0 ? 'green' : 'red'} trend={totalPnl > 0 ? 'up' : totalPnl < 0 ? 'down' : 'neutral'} />
        <StatCard label="Active Bots" value={`${activeBots.length} / ${bots.length}`} color="accent" />
        <StatCard label="Open Positions" value={openPositions} color="accent" />
        <StatCard label="Circuit Breakers" value={circuitBreakerLabel} color={circuitBreakerColor} />
        <StatCard
          label="Sentiment"
          value={sentimentScore.toFixed(2)}
          color={sentimentScore >= 0 ? 'green' : 'red'}
          trend={sentimentScore > 0 ? 'up' : sentimentScore < 0 ? 'down' : 'neutral'}
        />
      </div>

      {/* Bot Grid + Equity */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Bot Cards */}
        <div className="xl:col-span-2">
          <Panel title="Active Bots" subtitle={`${activeBots.length} bots running`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {bots.filter(b => b.status !== 'stopped').map(bot => (
                <div key={bot.id} className="rounded-lg border border-border bg-secondary/30 p-3 hover:bg-secondary/50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{bot.symbol}</span>
                      <StatusBadge
                        variant={bot.status === 'running' ? 'success' : bot.status === 'paused' ? 'warning' : 'danger'}
                        pulse={bot.status === 'running'}
                        size="sm"
                      >
                        {bot.status}
                      </StatusBadge>
                    </div>
                    <span className="font-mono text-sm">
                      {prices[bot.symbol] !== undefined
                        ? `$${prices[bot.symbol].toLocaleString(undefined, { maximumFractionDigits: 2 })}`
                        : '—'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <StatusBadge variant="info" size="sm">{bot.active_strategy || '—'}</StatusBadge>
                    <StatusBadge variant={bot.mode === 'auto' ? 'info' : 'neutral'} size="sm">{bot.mode}</StatusBadge>
                    {bot.regime && (
                      <StatusBadge variant={regimeColors[bot.regime] as "success" | "danger" | "warning" | "info" | "neutral"} size="sm">
                        {regimeIcons[bot.regime]} {bot.regime.toUpperCase()}
                      </StatusBadge>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-xs mb-2">
                    <div>
                      {bot.position ? (
                        <StatusBadge variant={bot.position.side === 'long' ? 'success' : 'danger'} size="sm">
                          {bot.position.side.toUpperCase()} {bot.position.unrealized_pnl >= 0 ? '+' : ''}{bot.position.unrealized_pnl.toFixed(2)}
                        </StatusBadge>
                      ) : (
                        <span className="text-muted-foreground">FLAT</span>
                      )}
                    </div>
                    <span className={cn('font-mono font-medium', bot.daily_pnl >= 0 ? 'text-success' : 'text-danger')}>
                      {bot.daily_pnl >= 0 ? '+' : ''}${bot.daily_pnl.toFixed(2)} ({bot.daily_pnl_pct.toFixed(2)}%)
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 pt-2 border-t border-border/50">
                    {bot.status === 'running' && (
                      <button
                        onClick={() => stopBot(bot.id).then(refreshBots).catch(console.error)}
                        className="px-2 py-1 rounded text-[11px] bg-warning/15 text-warning hover:bg-warning/25 transition-colors"
                        title="Pause (mapped to stop)"
                      >
                        <Pause className="h-3 w-3" />
                      </button>
                    )}
                    {bot.status === 'paused' && (
                      <button onClick={() => startBot(bot.id).then(refreshBots).catch(console.error)} className="px-2 py-1 rounded text-[11px] bg-success/15 text-success hover:bg-success/25 transition-colors">
                        <Play className="h-3 w-3" />
                      </button>
                    )}
                    <button onClick={() => stopBot(bot.id).then(refreshBots).catch(console.error)} className="px-2 py-1 rounded text-[11px] bg-danger/15 text-danger hover:bg-danger/25 transition-colors">
                      <Square className="h-3 w-3" />
                    </button>
                    <Link to="/bots" className="ml-auto px-2 py-1 rounded text-[11px] text-accent hover:bg-accent/10 transition-colors flex items-center gap-1">
                      Details <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        {/* Equity Curve */}
        <div>
          <Panel
            title="Equity Curve"
            actions={
              <div className="flex gap-1">
                {(['7D', '30D', '90D'] as const).map(r => (
                  <button
                    key={r}
                    onClick={() => setEquityRange(r)}
                    className={cn(
                      'px-2 py-0.5 rounded text-[11px] transition-colors',
                      equityRange === r ? 'bg-accent/15 text-accent' : 'text-muted-foreground hover:text-foreground'
                    )}
                  >
                    {r}
                  </button>
                ))}
              </div>
            }
          >
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={equityData}>
                  <defs>
                    <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(212 100% 67%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(212 100% 67%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" tick={false} axisLine={false} />
                  <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10, fill: 'hsl(215 8% 57%)' }} axisLine={false} tickLine={false} tickFormatter={(v: number) => `$${(v/1000).toFixed(1)}k`} />
                  <Tooltip
                    contentStyle={{ background: 'hsl(216 18% 11%)', border: '1px solid hsl(215 10% 22%)', borderRadius: 8, fontSize: 12 }}
                    labelFormatter={() => ''}
                    formatter={(value: number) => [`$${value.toFixed(2)}`, 'Equity']}
                  />
                  <Area type="monotone" dataKey="equity" stroke="hsl(212 100% 67%)" fill="url(#eqGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Panel>
        </div>
      </div>

      {/* Recent Trades + Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Panel title="Recent Trades" actions={<Link to="/history" className="text-[11px] text-accent hover:underline">View All</Link>}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border/50">
                  <th className="text-left py-2 font-medium text-muted-foreground">Time</th>
                  <th className="text-left py-2 font-medium text-muted-foreground">Symbol</th>
                  <th className="text-left py-2 font-medium text-muted-foreground">Side</th>
                  <th className="text-left py-2 font-medium text-muted-foreground">Strategy</th>
                  <th className="text-right py-2 font-medium text-muted-foreground">PnL</th>
                </tr>
              </thead>
              <tbody>
                {trades.filter(t => t.pnl !== undefined).slice(0, 10).map(trade => (
                  <tr key={trade.id} className="border-b border-border/30 hover:bg-secondary/30 cursor-pointer">
                    <td className="py-2 text-muted-foreground font-mono">{new Date(trade.timestamp).toLocaleTimeString()}</td>
                    <td className="py-2 font-medium">{trade.symbol}</td>
                    <td className="py-2">
                      <StatusBadge variant={trade.side === 'long' ? 'success' : 'danger'} size="sm">{trade.side.toUpperCase()}</StatusBadge>
                    </td>
                    <td className="py-2 text-muted-foreground">{trade.strategy}</td>
                    <td className={cn('py-2 text-right font-mono', (trade.pnl || 0) >= 0 ? 'text-success' : 'text-danger')}>
                      {(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Live Alerts" actions={<Link to="/intelligence" className="text-[11px] text-accent hover:underline">View All</Link>}>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {alerts.map((alert, i) => (
              <div key={i} className={cn(
                'rounded-md border p-2.5',
                alert.level === 'critical' ? 'border-danger/30 bg-danger/5' :
                alert.level === 'warning' ? 'border-warning/30 bg-warning/5' :
                'border-border bg-secondary/20'
              )}>
                <div className="flex items-center gap-2 mb-1">
                  <StatusBadge variant={alert.level === 'critical' ? 'danger' : alert.level === 'warning' ? 'warning' : 'info'} size="sm">
                    {alert.level}
                  </StatusBadge>
                  <span className="text-xs font-medium">{alert.title}</span>
                  <span className="ml-auto text-[10px] text-muted-foreground font-mono">
                    {Math.floor((Date.now() - alert.timestamp) / 60000)}m ago
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">{alert.body}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
