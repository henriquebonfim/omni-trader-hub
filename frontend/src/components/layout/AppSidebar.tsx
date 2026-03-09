import {
  LayoutDashboard, Bot, Brain, BarChart3, Target, Shield,
  ClipboardList, FlaskConical, Settings, TrendingUp, ChevronLeft, ChevronRight
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useState } from 'react';
import { mockBots } from '@/lib/mock-data';
import { useAppStore } from '@/stores/app-store';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/bots', icon: Bot, label: 'Bots & Assets' },
  { to: '/intelligence', icon: Brain, label: 'Intelligence' },
  { to: '/charts', icon: BarChart3, label: 'Charts' },
  { to: '/backtesting', icon: Target, label: 'Backtesting' },
  { to: '/risk', icon: Shield, label: 'Risk Monitor' },
  { to: '/history', icon: ClipboardList, label: 'Trade History' },
  { to: '/strategy-lab', icon: FlaskConical, label: 'Strategy Lab' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const storeBots = useAppStore((s) => s.bots);
  const bots = storeBots.length > 0 ? storeBots : mockBots;
  const activeBots = bots.filter(b => b.status === 'running');
  const totalPnl = activeBots.reduce((s, b) => s + b.daily_pnl, 0);
  const totalBalance = bots.reduce((s, b) => s + b.balance_allocated, 0);

  return (
    <aside className={cn(
      'flex flex-col border-r border-border bg-card shrink-0 transition-all duration-200',
      collapsed ? 'w-14' : 'w-[220px]'
    )}>
      {/* Nav items */}
      <nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-2.5 py-2 rounded-md text-[13px] transition-colors',
              isActive
                ? 'bg-accent/10 text-accent font-medium'
                : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
            )}
            title={label}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom summary */}
      {!collapsed && (
        <div className="border-t border-border p-3 space-y-1.5">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-muted-foreground">Active Bots</span>
            <span className="font-mono font-medium">{activeBots.length}</span>
          </div>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-muted-foreground">Today PnL</span>
            <span className={cn('font-mono font-medium', totalPnl >= 0 ? 'text-success' : 'text-danger')}>
              {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-muted-foreground">Total Balance</span>
            <span className="font-mono font-medium">${totalBalance.toLocaleString()}</span>
          </div>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-8 border-t border-border hover:bg-secondary/50 transition-colors"
      >
        {collapsed ? <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" /> : <ChevronLeft className="h-3.5 w-3.5 text-muted-foreground" />}
      </button>
    </aside>
  );
}
