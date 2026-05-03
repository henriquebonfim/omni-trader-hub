import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { fetchBots, startBot, stopBot, restartBot, manualOpenTrade, manualCloseTrade } from '@/domains/bot/api';
import { fetchSentiment } from '@/domains/market/api';
import { fetchEquitySnapshots, fetchTradeHistory } from '@/domains/trade/api';
import type { EquitySnapshot, Trade } from '@/domains/trade/types';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatCard } from '@/shared/ui/molecules/StatCard';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { ArrowRight, ArrowUpDown, Pause, Play, Square, TrendingUp, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { BotControlCard } from '@/features/bot/components/BotControlCard';
import { AIOverviewCard } from '@/features/intelligence/AIOverview';

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
  const bots = useAppStore(s => s.bots);
  const setBots = useAppStore(s => s.setBots);
  const livePrices = useAppStore(s => s.livePrices);
  const alerts = useAppStore(s => s.alerts);
  const wsStatus = useAppStore(s => s.wsStatus);

  const refreshBots = () => fetchBots().then(setBots).catch(console.error);

  const [trades, setTrades] = useState<Trade[]>([]);
  const [equityDataAll, setEquityDataAll] = useState<EquitySnapshot[]>([]);
  const [sentimentScore, setSentimentScore] = useState<number>(0);

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
      <AIOverviewCard />
      {/* Global Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard label="Portfolio Value" value={`$${totalValue.toLocaleString()}`} />
        <StatCard label="Today's PnL" value={`$${(totalPnl ?? 0).toFixed(2)}`} suffix={` (${(totalPnlPct ?? 0).toFixed(2)}%)`} color={totalPnl >= 0 ? 'green' : 'red'} trend={totalPnl > 0 ? 'up' : totalPnl < 0 ? 'down' : 'neutral'} />
        <StatCard label="Active Bots" value={`${activeBots.length} / ${bots.length}`} color="accent" />
        <StatCard label="Open Positions" value={openPositions} color="accent" />
        <StatCard label="Circuit Breakers" value={circuitBreakerLabel} color={circuitBreakerColor} />
        <StatCard
          label="Sentiment"
          value={(sentimentScore ?? 0).toFixed(2)}
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
                <BotControlCard key={bot.id} bot={bot} livePrice={livePrices[bot.symbol]} />
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
