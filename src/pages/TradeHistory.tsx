import { Panel } from '@/components/shared/Panel';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { StatCard } from '@/components/shared/StatCard';
import { mockTrades } from '@/lib/mock-data';
import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';

export default function TradeHistory() {
  const [sideFilter, setSideFilter] = useState<'all' | 'long' | 'short'>('all');
  const [actionFilter, setActionFilter] = useState<'all' | 'OPEN' | 'CLOSE'>('all');
  const [page, setPage] = useState(0);
  const perPage = 15;

  const filtered = useMemo(() => {
    return mockTrades.filter((t) => {
      if (sideFilter !== 'all' && t.side !== sideFilter) return false;
      if (actionFilter !== 'all' && t.action !== actionFilter) return false;
      return true;
    });
  }, [sideFilter, actionFilter]);

  const paged = filtered.slice(page * perPage, (page + 1) * perPage);
  const totalPages = Math.ceil(filtered.length / perPage);

  const closedTrades = mockTrades.filter((t) => t.action === 'CLOSE');
  const totalPnl = closedTrades.reduce((s, t) => s + (t.pnl ?? 0), 0);
  const wins = closedTrades.filter((t) => (t.pnl ?? 0) > 0).length;
  const losses = closedTrades.filter((t) => (t.pnl ?? 0) <= 0).length;

  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">📋 Trade History</h1>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Trades" value={closedTrades.length} />
        <StatCard label="Total P&L" value={totalPnl.toFixed(2)} prefix="$" variant={totalPnl >= 0 ? 'green' : 'red'} />
        <StatCard label="Win Rate" value={((wins / (wins + losses)) * 100).toFixed(1)} suffix="%" variant="green" />
        <StatCard label="W / L" value={`${wins} / ${losses}`} />
      </div>

      {/* Filters */}
      <Panel title="Filters" className="!py-0">
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex gap-1 items-center">
            <span className="text-xs text-muted-foreground mr-1">Side:</span>
            {(['all', 'long', 'short'] as const).map((f) => (
              <button key={f} onClick={() => { setSideFilter(f); setPage(0); }}
                className={`px-2 py-1 text-xs rounded capitalize ${sideFilter === f ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                {f}
              </button>
            ))}
          </div>
          <div className="flex gap-1 items-center">
            <span className="text-xs text-muted-foreground mr-1">Action:</span>
            {(['all', 'OPEN', 'CLOSE'] as const).map((f) => (
              <button key={f} onClick={() => { setActionFilter(f); setPage(0); }}
                className={`px-2 py-1 text-xs rounded ${actionFilter === f ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                {f}
              </button>
            ))}
          </div>
          <button onClick={() => { setSideFilter('all'); setActionFilter('all'); setPage(0); }}
            className="text-xs text-muted-foreground hover:text-foreground underline">Reset</button>
        </div>
      </Panel>

      {/* Table */}
      <Panel>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-muted-foreground border-b border-border">
                <th className="text-left py-2 px-2">Date</th>
                <th className="text-left py-2 px-2">Side</th>
                <th className="text-left py-2 px-2">Action</th>
                <th className="text-right py-2 px-2">Price</th>
                <th className="text-right py-2 px-2">Size</th>
                <th className="text-right py-2 px-2">P&L</th>
                <th className="text-left py-2 px-2">Reason</th>
              </tr>
            </thead>
            <tbody>
              {paged.map((t) => (
                <tr key={t.id} className="border-b border-border/50 hover:bg-accent/50 transition-colors">
                  <td className="py-2 px-2 font-mono text-muted-foreground">{new Date(t.timestamp).toLocaleDateString()}</td>
                  <td className="py-2 px-2">
                    <StatusBadge variant={t.side === 'long' ? 'success' : 'danger'}>{t.side.toUpperCase()}</StatusBadge>
                  </td>
                  <td className="py-2 px-2 text-foreground">{t.action}</td>
                  <td className="py-2 px-2 text-right font-mono text-foreground">${t.price.toFixed(2)}</td>
                  <td className="py-2 px-2 text-right font-mono text-foreground">{t.size.toFixed(4)}</td>
                  <td className={`py-2 px-2 text-right font-mono ${(t.pnl ?? 0) >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                    {t.action === 'CLOSE' ? `${(t.pnl ?? 0) >= 0 ? '+' : ''}$${(t.pnl ?? 0).toFixed(2)}` : '—'}
                  </td>
                  <td className="py-2 px-2 text-muted-foreground">{t.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-muted-foreground">{filtered.length} trades</span>
          <div className="flex gap-1">
            <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)} className="text-xs h-7 px-2">Prev</Button>
            <span className="text-xs text-muted-foreground flex items-center px-2">{page + 1}/{totalPages}</span>
            <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)} className="text-xs h-7 px-2">Next</Button>
          </div>
        </div>
      </Panel>
    </div>
  );
}
