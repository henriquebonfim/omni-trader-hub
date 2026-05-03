import { useAppStore } from '@/app/store/app-store';
import { cn } from '@/core/utils';
import { deleteBot, fetchBots, startBot, stopBot } from '@/domains/bot/api';
import { AddBotDrawer } from '@/domains/bot/components/AddBotDrawer';
import { BotDetailDrawer } from '@/domains/bot/components/BotDetailDrawer';
import { EmptyState } from '@/shared/ui/molecules/EmptyState';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { Bot, Pause, Play, Plus, Search, Square, Trash2 } from 'lucide-react';
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
