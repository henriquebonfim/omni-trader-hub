import { cn } from '@/core/utils';
import { useLocation, Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { icon: '📊', label: 'Live Dashboard', path: '/' },
  { icon: '🧠', label: 'Intelligence', path: '/intelligence' },
  { icon: '📈', label: 'Chart Analysis', path: '/charts' },
  { icon: '🎯', label: 'Backtesting', path: '/backtesting' },
  { icon: '⚙️', label: 'Trade Execution', path: '/execution' },
  { icon: '🛡️', label: 'Risk Monitor', path: '/risk' },
  { icon: '📋', label: 'Trade History', path: '/history' },
  { icon: '⚙️', label: 'Configuration', path: '/config' },
];

export function AppSidebar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const nav = (
    <nav className="flex flex-col gap-1 p-3">
      {navItems.map((item) => {
        const active = location.pathname === item.path;
        return (
          <Link
            key={item.path}
            to={item.path}
            onClick={() => setMobileOpen(false)}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
              active
                ? 'bg-primary/15 text-primary font-medium'
                : 'text-muted-foreground hover:text-foreground hover:bg-accent'
            )}
          >
            <span className="text-base">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-3 left-3 z-50 p-1 rounded-md bg-card border border-border"
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-background/80 backdrop-blur-sm" onClick={() => setMobileOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={cn(
        'fixed lg:sticky top-0 left-0 z-40 h-screen w-52 bg-card border-r border-border transition-transform lg:translate-x-0 shrink-0',
        mobileOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="h-12 flex items-center px-4 border-b border-border">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Navigation</span>
        </div>
        {nav}
      </aside>
    </>
  );
}
