import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { fetchCorrelationMatrix } from '@/domains/market/api';
import type { CorrelationMatrixData } from '@/domains/market/types';
import { fetchEquitySnapshots, fetchTradeHistory } from '@/domains/trade/api';
import type { EquitySnapshot, Trade } from '@/domains/trade/types';
import { CorrelationHeatmap } from '@/shared/ui/organisms/CorrelationHeatmap';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatCard } from '@/shared/ui/molecules/StatCard';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { AlertCircle, Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

export default function RiskMonitor() {
  const bots = useAppStore(s => s.bots);
  const activeBots = useMemo(() => bots.filter(b => b.status === 'running'), [bots]);
  const activeSymbols = useMemo(() => activeBots.map((b) => b.symbol), [activeBots]);
  const totalExposure = activeBots.reduce((s, b) => s + b.balance_allocated * b.leverage, 0);
  const totalAllocated = bots.reduce((s, b) => s + b.balance_allocated, 0);
  const openPositions = bots.filter(b => b.position).length;

  const [correlationData, setCorrelationData] = useState<CorrelationMatrixData | null>(null);
  const [loadingCorrelation, setLoadingCorrelation] = useState(true);
  const [errorCorrelation, setErrorCorrelation] = useState(false);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [equitySnapshots, setEquitySnapshots] = useState<EquitySnapshot[]>([]);

  useEffect(() => {
    fetchCorrelationMatrix({ timeframe: '1h', limit: 120, symbols: activeSymbols })
      .then((res) => {
        setCorrelationData(res);
        setErrorCorrelation(false);
      })
      .catch((e) => {
        console.error(e);
        setErrorCorrelation(true);
      })
      .finally(() => setLoadingCorrelation(false));
  }, [activeSymbols]);

  useEffect(() => {
    fetchTradeHistory({ limit: '500' })
      .then((res) => setTrades(res.trades))
      .catch(console.error);
    fetchEquitySnapshots()
      .then(setEquitySnapshots)
      .catch(console.error);
  }, []);

  const peakEquity = useMemo(
    () => (equitySnapshots.length > 0 ? Math.max(...equitySnapshots.map((s) => s.equity)) : 0),
    [equitySnapshots],
  );
  const currentEquity = useMemo(
    () => (equitySnapshots.length > 0 ? equitySnapshots[equitySnapshots.length - 1].equity : totalAllocated),
    [equitySnapshots, totalAllocated],
  );
  const drawdownPct = peakEquity > 0 ? ((currentEquity - peakEquity) / peakEquity) * 100 : 0;

  const tradePnls = useMemo(
    () => trades.filter((t) => typeof t.pnl === 'number').sort((a, b) => a.timestamp - b.timestamp).map((t) => t.pnl as number),
    [trades],
  );
  const winningTrades = tradePnls.filter((pnl) => pnl > 0).length;
  const losingTrades = tradePnls.filter((pnl) => pnl < 0).length;

  const { currentStreak, currentStreakSide, longestWinStreak, longestLossStreak } = useMemo(() => {
    if (tradePnls.length === 0) {
      return { currentStreak: 0, currentStreakSide: 'flat' as const, longestWinStreak: 0, longestLossStreak: 0 };
    }

    let longestWins = 0;
    let longestLosses = 0;
    let run = 0;
    let sign = 0;

    for (const pnl of tradePnls) {
      const nextSign = pnl > 0 ? 1 : pnl < 0 ? -1 : 0;
      if (nextSign === 0) continue;
      if (nextSign === sign) {
        run += 1;
      } else {
        sign = nextSign;
        run = 1;
      }
      if (sign > 0) longestWins = Math.max(longestWins, run);
      if (sign < 0) longestLosses = Math.max(longestLosses, run);
    }

    let tailRun = 0;
    let tailSign = 0;
    for (let i = tradePnls.length - 1; i >= 0; i -= 1) {
      const pnl = tradePnls[i];
      const nextSign = pnl > 0 ? 1 : pnl < 0 ? -1 : 0;
      if (nextSign === 0) continue;
      if (tailSign === 0) {
        tailSign = nextSign;
        tailRun = 1;
      } else if (tailSign === nextSign) {
        tailRun += 1;
      } else {
        break;
      }
    }

    return {
      currentStreak: tailRun,
      currentStreakSide: tailSign > 0 ? ('win' as const) : tailSign < 0 ? ('loss' as const) : ('flat' as const),
      longestWinStreak: longestWins,
      longestLossStreak: longestLosses,
    };
  }, [tradePnls]);

  const sizeMultiplier = currentStreakSide === 'win'
    ? Math.min(1 + currentStreak * 0.1, 1.5)
    : currentStreakSide === 'loss'
      ? Math.max(1 - currentStreak * 0.1, 0.5)
      : 1;

  const circuitBreakers = [
    {
      name: 'Daily Loss',
      limit: '-5%',
      current: `${drawdownPct.toFixed(1)}%`,
      current_pct: Math.min((Math.abs(drawdownPct) / 5) * 100, 100),
      status: Math.abs(drawdownPct) >= 5 ? 'triggered' : Math.abs(drawdownPct) >= 3 ? 'warning' : 'ok',
    },
    {
      name: 'Consecutive Losses',
      limit: '3 max',
      current: String(currentStreakSide === 'loss' ? currentStreak : 0),
      current_pct: Math.min(((currentStreakSide === 'loss' ? currentStreak : 0) / 3) * 100, 100),
      status: (currentStreakSide === 'loss' ? currentStreak : 0) >= 3 ? 'triggered' : (currentStreakSide === 'loss' ? currentStreak : 0) >= 2 ? 'warning' : 'ok',
    },
    {
      name: 'Win/Loss Ratio',
      limit: '>= 1.0',
      current: losingTrades > 0 ? (winningTrades / losingTrades).toFixed(2) : winningTrades > 0 ? 'INF' : '0.00',
      current_pct: Math.min((losingTrades > 0 ? (winningTrades / losingTrades) : 1) * 50, 100),
      status: losingTrades > 0 && winningTrades / losingTrades < 0.7 ? 'warning' : 'ok',
    },
  ] as const;

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Risk Monitor</h1>

      {/* Global Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Exposure" value={`$${totalExposure.toLocaleString()}`} color="accent" />
        <StatCard label="Allocated Capital" value={`$${totalAllocated.toLocaleString()}`} />
        <StatCard
          label="Combined Drawdown"
          value={`${drawdownPct >= 0 ? '+' : ''}${drawdownPct.toFixed(2)}%`}
          color={drawdownPct <= -5 ? 'red' : drawdownPct < 0 ? 'yellow' : 'green'}
          trend={drawdownPct < 0 ? 'down' : drawdownPct > 0 ? 'up' : 'neutral'}
        />
        <StatCard label="Open Positions" value={openPositions} color="accent" />
      </div>

      {/* Circuit Breakers */}
      <Panel title="Circuit Breakers" subtitle="Automated risk limits">
        <div className="space-y-3">
          {circuitBreakers.map(cb => (
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
                {cb.status === 'ok' ? 'OK' : cb.status === 'warning' ? 'WARN' : 'TRIPPED'}
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
                const exposurePct = totalAllocated > 0 ? (exposure / totalAllocated) * 100 : 0;
                return (
                  <tr key={bot.id} className="border-b border-border/50 hover:bg-secondary/30">
                    <td className="px-4 py-3 font-semibold">{bot.symbol}</td>
                    <td className="px-4 py-3 font-mono">${exposure.toLocaleString()} ({exposurePct.toFixed(0)}%)</td>
                    <td className="px-4 py-3 font-mono">{bot.leverage}×</td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={Number(liqDist) > 25 ? 'success' : 'warning'}>{liqDist}%</StatusBadge>
                    </td>
                    <td className={cn('px-4 py-3 font-mono', bot.daily_pnl_pct >= 0 ? 'text-success' : 'text-danger')}>
                      {bot.daily_pnl_pct >= 0 ? '+' : ''}{bot.daily_pnl_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={bot.daily_pnl_pct < -5 ? 'danger' : bot.daily_pnl_pct < -3 ? 'warning' : 'success'} size="sm">
                        {bot.daily_pnl_pct < -5 ? 'TRIPPED' : bot.daily_pnl_pct < -3 ? 'WARN' : 'OK'}
                      </StatusBadge>
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
              <span className="font-mono font-medium">${peakEquity.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Current Equity</span>
              <span className="font-mono font-medium">${currentEquity.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Drawdown</span>
              <span className={cn('font-mono', drawdownPct < 0 ? 'text-danger' : 'text-success')}>
                {drawdownPct >= 0 ? '+' : ''}{drawdownPct.toFixed(2)}%
              </span>
            </div>
            <div className="w-full h-3 rounded-full bg-secondary overflow-hidden">
              <div className={cn('h-full rounded-full', Math.abs(drawdownPct) >= 5 ? 'bg-danger' : 'bg-warning')} style={{ width: `${Math.min((Math.abs(drawdownPct) / 15) * 100, 100)}%` }} />
            </div>
            <p className="text-[10px] text-muted-foreground">Auto-deleverage at -15% | Current: {drawdownPct.toFixed(2)}%</p>
          </div>
        </Panel>

        <Panel title="Streak Tracking">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Current Streak</span>
              <StatusBadge variant={currentStreakSide === 'win' ? 'success' : currentStreakSide === 'loss' ? 'danger' : 'neutral'}>
                {currentStreak === 0 ? 'No streak' : `${currentStreak} ${currentStreakSide === 'win' ? 'Wins' : 'Losses'}`}
              </StatusBadge>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Longest Win Streak</span>
              <span className="font-mono font-medium text-success">{longestWinStreak}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Longest Loss Streak</span>
              <span className="font-mono font-medium text-danger">{longestLossStreak}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Size Multiplier</span>
              <span className="font-mono font-medium">{sizeMultiplier.toFixed(1)}×</span>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title="Asset Correlation Matrix" subtitle="Rolling return correlation (active bots)">
        {loadingCorrelation ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : errorCorrelation || !correlationData ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground py-2">
            <AlertCircle className="h-4 w-4 text-warning" />
            <span>Correlation matrix unavailable.</span>
          </div>
        ) : (
          <CorrelationHeatmap data={correlationData} />
        )}
      </Panel>
    </div>
  );
}
