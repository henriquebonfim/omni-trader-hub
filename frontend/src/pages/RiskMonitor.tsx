import { Panel } from '@/shared/components/Panel';
import { StatCard } from '@/shared/components/StatCard';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { mockBots } from '@/domains/bot/mocks';
import { mockCircuitBreakers } from '@/domains/risk/mocks';
import { cn } from '@/core/utils';
import { Shield, AlertTriangle } from 'lucide-react';

export default function RiskMonitor() {
  const bots = mockBots;
  const activeBots = bots.filter(b => b.status === 'running');
  const totalExposure = activeBots.reduce((s, b) => s + b.balance_allocated * b.leverage, 0);
  const totalAllocated = bots.reduce((s, b) => s + b.balance_allocated, 0);
  const openPositions = bots.filter(b => b.position).length;

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Risk Monitor</h1>

      {/* Global Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Exposure" value={`$${totalExposure.toLocaleString()}`} color="accent" />
        <StatCard label="Allocated Capital" value={`$${totalAllocated.toLocaleString()}`} />
        <StatCard label="Combined Drawdown" value="-2.1%" color="yellow" trend="down" />
        <StatCard label="Open Positions" value={openPositions} color="accent" />
      </div>

      {/* Circuit Breakers */}
      <Panel title="Circuit Breakers" subtitle="Automated risk limits">
        <div className="space-y-3">
          {mockCircuitBreakers.map(cb => (
            <div key={cb.name} className="flex items-center gap-4">
              <div className="w-36 text-xs font-medium">{cb.name}</div>
              <div className="flex-1">
                <div className="w-full h-2 rounded-full bg-secondary overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      cb.current_pct < 50 ? 'bg-success' : cb.current_pct < 80 ? 'bg-warning' : 'bg-danger'
                    )}
                    style={{ width: `${Math.min(cb.current_pct, 100)}%` }}
                  />
                </div>
              </div>
              <div className="w-20 text-xs font-mono text-right">{cb.current} / {cb.limit}</div>
              <StatusBadge
                variant={cb.status === 'ok' ? 'success' : cb.status === 'warning' ? 'warning' : 'danger'}
                size="sm"
              >
                {cb.status === 'ok' ? '✅ OK' : cb.status === 'warning' ? '⚠️ WARN' : '🛑 TRIPPED'}
              </StatusBadge>
            </div>
          ))}
        </div>
      </Panel>

      {/* Per-Bot Risk */}
      <Panel title="Per-Bot Risk" noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {['Bot', 'Exposure', 'Leverage', 'Liq. Distance', 'DD from HWM', 'CB Status'].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-medium text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {activeBots.map(bot => {
                const exposure = bot.balance_allocated * bot.leverage;
                const liqDist = (100 / bot.leverage).toFixed(0);
                return (
                  <tr key={bot.id} className="border-b border-border/50 hover:bg-secondary/30">
                    <td className="px-4 py-3 font-semibold">{bot.symbol}</td>
                    <td className="px-4 py-3 font-mono">${exposure.toLocaleString()} ({((exposure / totalAllocated) * 100).toFixed(0)}%)</td>
                    <td className="px-4 py-3 font-mono">{bot.leverage}×</td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={Number(liqDist) > 25 ? 'success' : 'warning'}>{liqDist}%</StatusBadge>
                    </td>
                    <td className={cn('px-4 py-3 font-mono', bot.daily_pnl_pct >= 0 ? 'text-success' : 'text-danger')}>
                      {bot.daily_pnl_pct >= 0 ? '+' : ''}{bot.daily_pnl_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant="success" size="sm">OK</StatusBadge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Drawdown Tracker + Streak */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Panel title="Drawdown Tracker">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Peak Equity</span>
              <span className="font-mono font-medium">$61,240 (Mar 5)</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Current Equity</span>
              <span className="font-mono font-medium">$59,950</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Drawdown</span>
              <span className="font-mono text-danger">-2.1%</span>
            </div>
            <div className="w-full h-3 rounded-full bg-secondary overflow-hidden">
              <div className="h-full bg-warning rounded-full" style={{ width: '21%' }} />
            </div>
            <p className="text-[10px] text-muted-foreground">Auto-deleverage at -15% | Current: -2.1%</p>
          </div>
        </Panel>

        <Panel title="Streak Tracking">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Current Streak</span>
              <StatusBadge variant="success">3 Wins</StatusBadge>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Longest Win Streak</span>
              <span className="font-mono font-medium text-success">8</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Longest Loss Streak</span>
              <span className="font-mono font-medium text-danger">4</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Size Multiplier</span>
              <span className="font-mono font-medium">1.0×</span>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
