import { useState } from 'react';
import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { StatCard } from '@/shared/components/StatCard';
import { mockTrades } from '@/domains/trade/mocks';
import { cn } from '@/core/utils';
import { Download, ChevronDown, ChevronUp, Search } from 'lucide-react';
import type { Trade } from '@/domains/trade/types';

import { fetchTradeHistory } from '@/domains/trade/api';
import { useEffect } from 'react';

export default function TradeHistory() {
  const [period, setPeriod] = useState<'today' | 'week' | 'month' | 'all'>('all');
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<keyof Trade>('timestamp');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const [expanded, setExpanded] = useState<number | null>(null);
  const perPage = 20;
  
  const [trades, setTrades] = useState<Trade[]>(mockTrades);

  useEffect(() => {
    fetchTradeHistory({ limit: '500' }).then(res => {
      if (res && res.trades && res.trades.length > 0) setTrades(res.trades);
    }).catch(console.error);
  }, []);

  const closedTrades = trades.filter(t => t.pnl !== undefined);
  const filtered = closedTrades.filter(t =>
    t.symbol.toLowerCase().includes(search.toLowerCase()) ||
    t.strategy.toLowerCase().includes(search.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    if (aVal === undefined || bVal === undefined) return 0;
    return sortDir === 'asc' ? (aVal > bVal ? 1 : -1) : (aVal < bVal ? 1 : -1);
  });

  const paginated = sorted.slice(page * perPage, (page + 1) * perPage);
  const totalPages = Math.ceil(sorted.length / perPage);

  const totalPnl = closedTrades.reduce((s, t) => s + (t.pnl || 0), 0);
  const wins = closedTrades.filter(t => (t.pnl || 0) > 0).length;
  const winRate = closedTrades.length > 0 ? (wins / closedTrades.length) * 100 : 0;

  const toggleSort = (field: keyof Trade) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir('desc'); }
  };

  const SortIcon = ({ field }: { field: keyof Trade }) => (
    sortField === field ? (sortDir === 'asc' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />) : null
  );

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Trade History</h1>
        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-border text-xs text-muted-foreground hover:text-foreground transition-colors">
          <Download className="h-3.5 w-3.5" /> Export CSV
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard label="Total Trades" value={closedTrades.length} />
        <StatCard label="Total PnL" value={`$${totalPnl.toFixed(2)}`} color={totalPnl >= 0 ? 'green' : 'red'} />
        <StatCard label="Win Rate" value={`${winRate.toFixed(1)}%`} color={winRate >= 50 ? 'green' : 'red'} />
        <StatCard label="Avg Win" value={`$${(closedTrades.filter(t => (t.pnl||0) > 0).reduce((s,t) => s+(t.pnl||0), 0) / Math.max(wins, 1)).toFixed(2)}`} color="green" />
        <StatCard label="Avg Loss" value={`$${(closedTrades.filter(t => (t.pnl||0) < 0).reduce((s,t) => s+(t.pnl||0), 0) / Math.max(closedTrades.length - wins, 1)).toFixed(2)}`} color="red" />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Filter by symbol or strategy..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-md border border-border bg-secondary/30 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-accent"
          />
        </div>
        <div className="flex gap-1">
          {(['today', 'week', 'month', 'all'] as const).map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={cn(
                'px-2.5 py-1.5 rounded-md text-[11px] font-medium transition-colors capitalize',
                period === p ? 'bg-accent/15 text-accent' : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <Panel noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border">
                {[
                  { key: 'timestamp', label: 'Time' },
                  { key: 'symbol', label: 'Symbol' },
                  { key: 'side', label: 'Side' },
                  { key: 'strategy', label: 'Strategy' },
                  { key: 'price', label: 'Price' },
                  { key: 'size', label: 'Size' },
                  { key: 'pnl', label: 'PnL' },
                  { key: 'reason', label: 'Reason' },
                ].map(col => (
                  <th
                    key={col.key}
                    className="text-left px-4 py-3 font-medium text-muted-foreground cursor-pointer hover:text-foreground whitespace-nowrap"
                    onClick={() => toggleSort(col.key as keyof Trade)}
                  >
                    <span className="flex items-center gap-1">{col.label} <SortIcon field={col.key as keyof Trade} /></span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginated.map(trade => (
                <React.Fragment key={trade.id}>
                  <tr
                    className="border-b border-border/30 hover:bg-secondary/30 cursor-pointer"
                    onClick={() => setExpanded(expanded === trade.id ? null : trade.id)}
                  >
                    <td className="px-4 py-2.5 font-mono text-muted-foreground">{new Date(trade.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-2.5 font-medium">{trade.symbol}</td>
                    <td className="px-4 py-2.5">
                      <StatusBadge variant={trade.side === 'long' ? 'success' : 'danger'} size="sm">{trade.side.toUpperCase()}</StatusBadge>
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">{trade.strategy}</td>
                    <td className="px-4 py-2.5 font-mono">${trade.price.toFixed(2)}</td>
                    <td className="px-4 py-2.5 font-mono">{trade.size.toFixed(4)}</td>
                    <td className={cn('px-4 py-2.5 font-mono', (trade.pnl || 0) >= 0 ? 'text-success' : 'text-danger')}>
                      {(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toFixed(2)}
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">{trade.reason}</td>
                  </tr>
                  {expanded === trade.id && (
                    <tr className="bg-secondary/20">
                      <td colSpan={8} className="px-4 py-3">
                        <div className="grid grid-cols-4 gap-3 text-[11px]">
                          <div><span className="text-muted-foreground">Notional:</span> <span className="font-mono">${trade.notional.toFixed(2)}</span></div>
                          <div><span className="text-muted-foreground">Fee:</span> <span className="font-mono">${trade.fee.toFixed(2)}</span></div>
                          <div><span className="text-muted-foreground">PnL %:</span> <span className={cn('font-mono', (trade.pnl_pct || 0) >= 0 ? 'text-success' : 'text-danger')}>{(trade.pnl_pct || 0).toFixed(2)}%</span></div>
                          <div><span className="text-muted-foreground">Bot:</span> <span className="font-mono">{trade.bot_id}</span></div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <span className="text-[11px] text-muted-foreground">{sorted.length} trades</span>
          <div className="flex gap-1">
            <button disabled={page === 0} onClick={() => setPage(p => p - 1)} className="px-2 py-1 rounded border border-border text-[11px] disabled:opacity-30">Prev</button>
            <span className="px-2 py-1 text-[11px] text-muted-foreground">{page + 1} / {totalPages}</span>
            <button disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)} className="px-2 py-1 rounded border border-border text-[11px] disabled:opacity-30">Next</button>
          </div>
        </div>
      </Panel>
    </div>
  );
}
