import { StatCard } from '@/core/shared/StatCard';
import { Panel } from '@/core/shared/Panel';
import { StatusBadge } from '@/core/shared/StatusBadge';
import { SentimentEmoji } from '@/core/shared/SentimentEmoji';
import { CycleMessage } from '@/core/api/ws';
import { mockEquityData } from '@/core/api/mock-data';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useState } from 'react';
import { Play, Square, AlertTriangle } from 'lucide-react';
import { Button } from '@/core/ui/button';
import { useNavigate } from 'react-router-dom';

interface DashboardProps {
  data: CycleMessage;
}

export default function Dashboard({ data }: DashboardProps) {
  const [timeframe, setTimeframe] = useState<'1D' | '7D' | '30D' | 'ALL'>('7D');
  const [botRunning, setBotRunning] = useState(true);
  const navigate = useNavigate();

  const equityData = {
    '1D': mockEquityData.slice(-1),
    '7D': mockEquityData.slice(-7),
    '30D': mockEquityData,
    'ALL': mockEquityData,
  }[timeframe];

  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">📊 Live Dashboard</h1>

      {data.circuit_breaker && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-trading-red/10 border border-trading-red/30 text-trading-red text-sm">
          <AlertTriangle className="h-4 w-4" />
          Circuit Breaker Active — Trading is paused
        </div>
      )}

      {/* Hero stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Price" value={data.price.toFixed(2)} prefix="$" variant="accent" />
        <StatCard label="Signal" value={data.signal} variant={data.signal === 'LONG' ? 'green' : data.signal === 'SHORT' ? 'red' : 'default'} />
        <StatCard label="Position" value={data.position ?? 'FLAT'} variant={data.position === 'long' ? 'green' : data.position === 'short' ? 'red' : 'default'} />
        <StatCard label="Balance" value={data.balance.toFixed(2)} prefix="$" variant="accent" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Daily P&L" value={data.daily_pnl.toFixed(2)} prefix="$" trend={data.daily_pnl >= 0 ? 'up' : 'down'} variant={data.daily_pnl >= 0 ? 'green' : 'red'} />
        <StatCard label="Daily P&L %" value={data.daily_pnl_pct.toFixed(2)} suffix="%" trend={data.daily_pnl_pct >= 0 ? 'up' : 'down'} variant={data.daily_pnl_pct >= 0 ? 'green' : 'red'} />
        
        {/* Mini Sentiment Widget */}
        <div
          className="rounded-lg bg-card border border-border p-4 cursor-pointer hover:bg-accent transition-colors"
          onClick={() => navigate('/intelligence')}
        >
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Sentiment</p>
          <div className="flex items-center gap-2">
            <SentimentEmoji score={data.sentiment ?? 0} size="sm" />
            <span className={`text-xl font-bold tabular-nums ${(data.sentiment ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
              {(data.sentiment ?? 0) > 0 ? '+' : ''}{(data.sentiment ?? 0).toFixed(2)}
            </span>
          </div>
        </div>

        <div className="rounded-lg bg-card border border-border p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Crisis Mode</p>
          <StatusBadge variant={data.crisis_mode ? 'danger' : 'success'} size="md">
            {data.crisis_mode ? '🔴 ACTIVE' : '🟢 NORMAL'}
          </StatusBadge>
        </div>
      </div>

      {/* Bot Control + Equity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Panel title="Bot Control" className="lg:col-span-1">
          <div className="space-y-4">
            <div className="flex gap-2">
              <Button
                onClick={() => setBotRunning(true)}
                disabled={botRunning}
                className="flex-1 bg-trading-green/20 text-trading-green hover:bg-trading-green/30 border border-trading-green/30"
                variant="outline"
              >
                <Play className="h-4 w-4 mr-1" /> Start
              </Button>
              <Button
                onClick={() => setBotRunning(false)}
                disabled={!botRunning}
                className="flex-1 bg-trading-red/20 text-trading-red hover:bg-trading-red/30 border border-trading-red/30"
                variant="outline"
              >
                <Square className="h-4 w-4 mr-1" /> Stop
              </Button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Strategy</span><span className="text-foreground">ADX Trend</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Leverage</span><span className="text-foreground">3.0×</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Position Size</span><span className="text-foreground">2.0%</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Status</span>
                <StatusBadge variant={botRunning ? 'success' : 'neutral'}>{botRunning ? 'Running' : 'Stopped'}</StatusBadge>
              </div>
            </div>
          </div>
        </Panel>

        <Panel
          title="Equity Curve"
          className="lg:col-span-2"
          actions={
            <div className="flex gap-1">
              {(['1D', '7D', '30D', 'ALL'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-2 py-1 text-xs rounded ${timeframe === tf ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                >
                  {tf}
                </button>
              ))}
            </div>
          }
        >
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(215, 14%, 18%)" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(215, 10%, 55%)' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 10, fill: 'hsl(215, 10%, 55%)' }} tickLine={false} axisLine={false} width={60} tickFormatter={(v) => `$${v.toLocaleString()}`} />
                <Tooltip
                  contentStyle={{ background: 'hsl(215, 25%, 11%)', border: '1px solid hsl(215, 14%, 22%)', borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: 'hsl(215, 10%, 55%)' }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Balance']}
                />
                <Line type="monotone" dataKey="balance" stroke="hsl(140, 60%, 52%)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      {/* Quick Stats */}
      <Panel title="Quick Stats">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard label="Today's Trades" value={7} />
          <StatCard label="Win Rate" value="58.2" suffix="%" variant="green" />
          <StatCard label="Sharpe Ratio" value={1.42} variant="accent" />
          <StatCard label="Max Drawdown" value="-8.3" suffix="%" variant="red" />
          <StatCard label="Week's Trades" value={34} />
          <StatCard label="Avg Return" value="+1.8" suffix="%" variant="green" />
          <StatCard label="Profit Factor" value={1.87} variant="accent" />
          <StatCard label="Circuit Breaker" value={data.circuit_breaker ? 'Active' : 'Inactive'} variant={data.circuit_breaker ? 'red' : 'green'} />
        </div>
      </Panel>
    </div>
  );
}
