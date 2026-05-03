import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { fetchBots, restartBot, manualOpenTrade, manualCloseTrade } from '@/domains/bot/api';
import { fetchStrategies } from '@/domains/strategy/api';
import type { Strategy } from '@/domains/strategy/types';
import { fetchTradeHistory } from '@/domains/trade/api';
import type { Trade } from '@/domains/trade/types';
import { EmptyState } from '@/shared/ui/molecules/EmptyState';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { Bot, X } from 'lucide-react';
import { useEffect, useState } from 'react';

interface BotDetailDrawerProps {
  botId: string;
  onClose: () => void;
}

export function BotDetailDrawer({ botId, onClose }: BotDetailDrawerProps) {
  const storeBots = useAppStore(s => s.bots);
  const setBots = useAppStore(s => s.setBots);
  const bots = storeBots;
  const bot = bots.find(b => b.id === botId);
  const [tab, setTab] = useState<'overview' | 'position' | 'trades' | 'strategy' | 'risk'>('overview');
  const [trades, setTrades] = useState<Trade[]>([]);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (!bot) return;
    fetchTradeHistory({ symbol: bot.symbol, limit: '50' })
      .then(res => setTrades(res.trades))
      .catch(console.error);
    fetchStrategies()
      .then(all => setStrategy(all.find(s => s.name === bot.active_strategy) ?? null))
      .catch(console.error);
  }, [bot?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!bot) return null;

  const refresh = () => fetchBots().then(setBots).catch(console.error);

  const handleRestart = async () => {
    setProcessing(true);
    try {
      await restartBot(botId);
      await refresh();
    } finally {
      setProcessing(false);
    }
  };

  const handleManualOpen = async (side: 'long' | 'short') => {
    setProcessing(true);
    try {
      await manualOpenTrade(botId, side);
      await refresh();
    } finally {
      setProcessing(false);
    }
  };

  const handleManualClose = async () => {
    setProcessing(true);
    try {
      await manualCloseTrade(botId);
      await refresh();
    } finally {
      setProcessing(false);
    }
  };

  const closedTrades = trades.filter(t => t.action === 'CLOSE');
  const wins = closedTrades.filter(t => (t.pnl ?? 0) > 0).length;
  const losses = closedTrades.filter(t => (t.pnl ?? 0) <= 0 && t.pnl !== undefined).length;
  const winRate = closedTrades.length > 0 ? ((wins / closedTrades.length) * 100).toFixed(1) : '—';
  let lossStreak = 0;
  for (const t of closedTrades) {
    if ((t.pnl ?? 0) < 0) lossStreak++;
    else break;
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-card border-l border-border h-full overflow-y-auto animate-fade-in">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h2 className="text-sm font-semibold">{bot.symbol}</h2>
            <div className="flex items-center gap-2 mt-1">
              <StatusBadge variant={bot.status === 'running' ? 'success' : 'neutral'} pulse={bot.status === 'running'}>{bot.status}</StatusBadge>
              <StatusBadge variant="info">{bot.mode}</StatusBadge>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-secondary transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border px-4">
          {(['overview', 'position', 'trades', 'strategy', 'risk'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                'px-3 py-2.5 text-xs font-medium border-b-2 transition-colors capitalize',
                tab === t ? 'border-accent text-accent' : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="p-4 space-y-4">
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2 pb-4 border-b border-border/50">
            <button
              onClick={handleRestart}
              disabled={processing}
              className="px-3 py-1.5 rounded-md border border-border bg-secondary/30 text-[11px] font-medium hover:bg-secondary/50 transition-colors disabled:opacity-50"
            >
              Restart Bot
            </button>
            {bot.status === 'running' && !bot.position && (
              <>
                <button
                  onClick={() => handleManualOpen('long')}
                  disabled={processing}
                  className="px-3 py-1.5 rounded-md border border-success/30 bg-success/5 text-success text-[11px] font-medium hover:bg-success/10 transition-colors disabled:opacity-50"
                >
                  Manual Long
                </button>
                <button
                  onClick={() => handleManualOpen('short')}
                  disabled={processing}
                  className="px-3 py-1.5 rounded-md border border-danger/30 bg-danger/5 text-danger text-[11px] font-medium hover:bg-danger/10 transition-colors disabled:opacity-50"
                >
                  Manual Short
                </button>
              </>
            )}
            {bot.position && (
              <button
                onClick={handleManualClose}
                disabled={processing}
                className="px-3 py-1.5 rounded-md border border-warning/30 bg-warning/5 text-warning text-[11px] font-medium hover:bg-warning/10 transition-colors disabled:opacity-50"
              >
                Close Position
              </button>
            )}
          </div>

          {tab === 'overview' && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <StatCardMini label="Strategy" value={bot.active_strategy || '—'} />
                <StatCardMini label="Regime" value={bot.regime?.toUpperCase() || '—'} />
                <StatCardMini label="Daily PnL" value={`$${bot.daily_pnl.toFixed(2)}`} color={bot.daily_pnl >= 0 ? 'text-success' : 'text-danger'} />
                <StatCardMini label="Balance" value={`$${bot.balance_allocated.toLocaleString()}`} />
                <StatCardMini label="Leverage" value={`${bot.leverage}×`} />
                <StatCardMini label="Created" value={new Date(bot.created_at).toLocaleDateString()} />
              </div>
            </>
          )}
          {tab === 'position' && (
            bot.position ? (
              <div className="grid grid-cols-2 gap-3">
                <StatCardMini label="Side" value={bot.position.side.toUpperCase()} color={bot.position.side === 'long' ? 'text-success' : 'text-danger'} />
                <StatCardMini label="Entry Price" value={`$${bot.position.entry_price.toLocaleString()}`} />
                <StatCardMini label="Size" value={bot.position.size.toString()} />
                <StatCardMini label="Unrealized PnL" value={`$${bot.position.unrealized_pnl.toFixed(2)}`} color={bot.position.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'} />
                <StatCardMini label="Stop Loss" value={`$${bot.position.stop_loss.toLocaleString()}`} />
                <StatCardMini label="Take Profit" value={`$${bot.position.take_profit.toLocaleString()}`} />
              </div>
            ) : (
              <EmptyState icon={Bot} title="No open position" description="This bot has no active position" />
            )
          )}
          {tab === 'trades' && (
            trades.length === 0 ? (
              <EmptyState icon={Bot} title="No trades yet" description={`No trade history found for ${bot.symbol}`} />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border">
                      {['Time', 'Side', 'Action', 'Price', 'Size', 'PnL'].map(h => (
                        <th key={h} className="text-left px-2 py-2 font-medium text-muted-foreground">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {trades.slice(0, 30).map(t => (
                      <tr key={t.id} className="border-b border-border/50 hover:bg-secondary/20">
                        <td className="px-2 py-2 text-muted-foreground">{new Date(t.timestamp).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</td>
                        <td className="px-2 py-2">
                          <StatusBadge variant={t.side === 'long' ? 'success' : 'danger'} size="sm">{t.side}</StatusBadge>
                        </td>
                        <td className="px-2 py-2">
                          <StatusBadge variant={t.action === 'OPEN' ? 'info' : 'neutral'} size="sm">{t.action}</StatusBadge>
                        </td>
                        <td className="px-2 py-2 font-mono">${t.price.toLocaleString()}</td>
                        <td className="px-2 py-2 font-mono">{t.size}</td>
                        <td className={cn('px-2 py-2 font-mono', t.pnl !== undefined ? (t.pnl >= 0 ? 'text-success' : 'text-danger') : 'text-muted-foreground')}>
                          {t.pnl !== undefined ? `${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(2)}` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
          {tab === 'strategy' && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <StatCardMini label="Active Strategy" value={bot.active_strategy || 'None'} />
                <StatCardMini label="Mode" value={bot.mode === 'auto' ? 'Auto-selected' : 'Manually locked'} />
                <StatCardMini label="Regime Affinity" value={strategy?.regime_affinity?.toUpperCase() ?? bot.regime?.toUpperCase() ?? '—'} />
                <StatCardMini label="Win Rate" value={strategy?.win_rate !== undefined ? `${strategy.win_rate}%` : '—'} />
                <StatCardMini label="Sharpe" value={strategy?.sharpe !== undefined ? strategy.sharpe.toFixed(2) : '—'} />
                <StatCardMini label="Active Bots" value={strategy?.active_bots?.toString() ?? '—'} />
              </div>
              {strategy?.description && (
                <div className="rounded-md border border-border/50 bg-secondary/10 p-3">
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{strategy.description}</p>
                </div>
              )}
            </div>
          )}
          {tab === 'risk' && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <StatCardMini label="Exposure" value={`$${(bot.balance_allocated * bot.leverage).toLocaleString()}`} />
                <StatCardMini label="Leverage" value={`${bot.leverage}×`} />
                <StatCardMini label="Daily PnL %" value={`${bot.daily_pnl_pct.toFixed(2)}%`} color={bot.daily_pnl_pct >= 0 ? 'text-success' : 'text-danger'} />
                <StatCardMini label="Win Rate" value={winRate !== '—' ? `${winRate}%` : '—'} color={parseFloat(winRate) >= 50 ? 'text-success' : 'text-danger'} />
                <StatCardMini label="Wins / Losses" value={closedTrades.length > 0 ? `${wins} / ${losses}` : '—'} />
                <StatCardMini label="Loss Streak" value={lossStreak > 0 ? lossStreak.toString() : '0'} color={lossStreak >= 3 ? 'text-danger' : lossStreak >= 2 ? 'text-warning' : undefined} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCardMini({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-md border border-border bg-secondary/30 p-3">
      <p className="text-[11px] text-muted-foreground mb-0.5">{label}</p>
      <p className={cn('text-sm font-medium font-mono', color || 'text-foreground')}>{value}</p>
    </div>
  );
}
