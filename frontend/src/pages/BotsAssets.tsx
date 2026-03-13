import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { createBot, deleteBot, fetchBots, startBot, stopBot } from '@/domains/bot/api';
import { fetchMarkets } from '@/domains/market/api';
import type { MarketPair } from '@/domains/market/types';
import { fetchStrategies } from '@/domains/strategy/api';
import type { Strategy } from '@/domains/strategy/types';
import { fetchTradeHistory } from '@/domains/trade/api';
import type { Trade } from '@/domains/trade/types';
import { EmptyState } from '@/shared/components/EmptyState';
import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { Bot, Pause, Play, Plus, Search, Square, Trash2, X } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function BotsAssets() {
  const storeBots = useAppStore(s => s.bots);
  const setBots = useAppStore(s => s.setBots);
  const bots = storeBots;

  const [showAddDrawer, setShowAddDrawer] = useState(false);
  const [selectedBot, setSelectedBot] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (storeBots.length === 0) {
      fetchBots().then(setBots).catch(console.error);
    }
  }, [setBots, storeBots.length]);

  const filteredBots = bots.filter(b =>
    b.symbol.toLowerCase().includes(search.toLowerCase()) ||
    b.active_strategy.toLowerCase().includes(search.toLowerCase())
  );

  const handleStartBot = (id: string) => {
    startBot(id).catch(console.error);
  };

  const handleStopBot = (id: string) => {
    stopBot(id).catch(console.error);
  };

  const handleDeleteBot = (id: string) => {
    deleteBot(id).then(() => fetchBots().then(setBots)).catch(console.error);
  };

  const handleRefreshBots = () => {
    fetchBots().then(setBots).catch(console.error);
  };

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Bots & Assets</h1>
          <p className="text-xs text-muted-foreground">Manage your trading bots across all assets</p>
        </div>
        <button
          onClick={() => setShowAddDrawer(true)}
          className="flex items-center gap-2 px-3 py-2 rounded-md bg-accent text-primary-foreground text-xs font-medium hover:bg-accent/90 transition-colors"
        >
          <Plus className="h-3.5 w-3.5" /> Add Bot
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search bots by symbol or strategy..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 rounded-md border border-border bg-secondary/30 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent"
        />
      </div>

      {/* Table */}
      <Panel noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {['Symbol', 'Status', 'Mode', 'Strategy', 'Regime', 'Position', 'Daily PnL', 'Balance', 'Leverage', 'Actions'].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-medium text-muted-foreground whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredBots.map(bot => (
                <tr key={bot.id} className="border-b border-border/50 hover:bg-secondary/30 cursor-pointer" onClick={() => setSelectedBot(bot.id)}>
                  <td className="px-4 py-3 font-semibold">{bot.symbol}</td>
                  <td className="px-4 py-3">
                    <StatusBadge
                      variant={bot.status === 'running' ? 'success' : bot.status === 'paused' ? 'warning' : bot.status === 'error' ? 'danger' : 'neutral'}
                      pulse={bot.status === 'running'}
                    >
                      {bot.status}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge variant={bot.mode === 'auto' ? 'info' : 'neutral'}>{bot.mode}</StatusBadge>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{bot.active_strategy || '—'}</td>
                  <td className="px-4 py-3">
                    {bot.regime ? (
                      <span className={cn('text-xs font-medium uppercase', `regime-${bot.regime}`)}>{bot.regime}</span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    {bot.position ? (
                      <StatusBadge variant={bot.position.side === 'long' ? 'success' : 'danger'}>
                        {bot.position.side.toUpperCase()} {bot.position.unrealized_pnl >= 0 ? '+' : ''}{bot.position.unrealized_pnl.toFixed(2)}%
                      </StatusBadge>
                    ) : (
                      <span className="text-muted-foreground">FLAT</span>
                    )}
                  </td>
                  <td className={cn('px-4 py-3 font-mono', bot.daily_pnl >= 0 ? 'text-success' : 'text-danger')}>
                    {bot.daily_pnl >= 0 ? '+' : ''}${bot.daily_pnl.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 font-mono">${bot.balance_allocated.toLocaleString()}</td>
                  <td className="px-4 py-3 font-mono">{bot.leverage}×</td>
                  <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                    <div className="flex items-center gap-1">
                      {bot.status === 'running' && (
                        <button
                          className="p-1.5 rounded hover:bg-warning/15 text-warning transition-colors"
                          title="Pause (mapped to stop)"
                          onClick={(e) => { e.stopPropagation(); handleStopBot(bot.id); }}
                        >
                          <Pause className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {(bot.status === 'paused' || bot.status === 'stopped') && (
                        <button className="p-1.5 rounded hover:bg-success/15 text-success transition-colors" title="Start" onClick={(e) => { e.stopPropagation(); handleStartBot(bot.id); }}>
                          <Play className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {bot.status !== 'stopped' && (
                        <button className="p-1.5 rounded hover:bg-danger/15 text-danger transition-colors" title="Stop" onClick={(e) => { e.stopPropagation(); handleStopBot(bot.id); }}>
                          <Square className="h-3.5 w-3.5" />
                        </button>
                      )}
                      <button className="p-1.5 rounded hover:bg-danger/15 text-danger/70 transition-colors" title="Delete"
                        onClick={(e) => { e.stopPropagation(); handleDeleteBot(bot.id); }}>
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredBots.length === 0 && (
            <EmptyState icon={Bot} title="No bots found" description="Create your first bot to start trading" />
          )}
        </div>
      </Panel>

      {/* Add Bot Drawer */}
      {showAddDrawer && <AddBotDrawer onClose={() => setShowAddDrawer(false)} onCreated={handleRefreshBots} />}

      {/* Bot Detail Drawer */}
      {selectedBot && <BotDetailDrawer botId={selectedBot} onClose={() => setSelectedBot(null)} />}
    </div>
  );
}

function AddBotDrawer({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [symbol, setSymbol] = useState('');
  const [mode, setMode] = useState<'auto' | 'manual'>('auto');
  const [leverage, setLeverage] = useState(3);
  const [allocation, setAllocation] = useState(10);
  const [marketSearch, setMarketSearch] = useState('');
  const [markets, setMarkets] = useState<MarketPair[]>([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchMarkets().then(setMarkets).catch(console.error);
  }, []);

  const filteredMarkets = markets.filter(m =>
    m.symbol.toLowerCase().includes(marketSearch.toLowerCase())
  );

  const handleCreate = async () => {
    if (!symbol) return;
    setCreating(true);
    try {
      await createBot({ symbol, mode, leverage, balance_allocated: allocation } as any);
      onCreated();
      onClose();
    } catch (e) {
      console.error('createBot error', e);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-card border-l border-border h-full overflow-y-auto animate-fade-in">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-sm font-semibold">Add New Bot</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-secondary transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Symbol */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Symbol</label>
            <input
              placeholder="Search markets..."
              value={marketSearch}
              onChange={e => setMarketSearch(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-border bg-secondary/30 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent mb-2"
            />
            <div className="max-h-40 overflow-y-auto border border-border rounded-md">
              {filteredMarkets.map(m => (
                <button
                  key={m.symbol}
                  onClick={() => { setSymbol(m.symbol); setMarketSearch(m.symbol); }}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 text-xs hover:bg-secondary/50 transition-colors',
                    symbol === m.symbol && 'bg-accent/10 text-accent'
                  )}
                >
                  <span className="font-medium">{m.symbol}</span>
                  <span className="text-muted-foreground font-mono">${m.last_price.toLocaleString()}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Mode */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Mode</label>
            <div className="flex gap-2">
              {(['auto', 'manual'] as const).map(m => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={cn(
                    'flex-1 py-2 rounded-md border text-xs font-medium transition-colors',
                    mode === m ? 'border-accent bg-accent/10 text-accent' : 'border-border text-muted-foreground hover:text-foreground'
                  )}
                >
                  {m === 'auto' ? 'Auto (bot selects)' : 'Manual (lock strategy)'}
                </button>
              ))}
            </div>
          </div>

          {/* Leverage */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Leverage: {leverage}×</label>
            <input type="range" min={1} max={10} value={leverage} onChange={e => setLeverage(Number(e.target.value))}
              className="w-full accent-accent" />
          </div>

          {/* Allocation */}
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Allocation: {allocation}%</label>
            <input type="range" min={1} max={50} value={allocation} onChange={e => setAllocation(Number(e.target.value))}
              className="w-full accent-accent" />
          </div>

          <button
            onClick={handleCreate}
            disabled={!symbol || creating}
            className="w-full py-2.5 rounded-md bg-accent text-primary-foreground text-xs font-semibold hover:bg-accent/90 transition-colors disabled:opacity-60"
          >
            {creating ? 'Creating…' : 'Create Bot'}
          </button>
        </div>
      </div>
    </div>
  );
}

function BotDetailDrawer({ botId, onClose }: { botId: string; onClose: () => void }) {
  const storeBots = useAppStore(s => s.bots);
  const bots = storeBots;
  const bot = bots.find(b => b.id === botId);
  const [tab, setTab] = useState<'overview' | 'position' | 'trades' | 'strategy' | 'risk'>('overview');
  const [trades, setTrades] = useState<Trade[]>([]);
  const [strategy, setStrategy] = useState<Strategy | null>(null);

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
