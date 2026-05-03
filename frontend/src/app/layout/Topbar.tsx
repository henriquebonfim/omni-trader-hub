import { useAppStore } from '@/app/store/app-store';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { Activity, Bell, ChevronDown, Settings, Wifi, WifiOff, LogOut } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { clearApiKey } from '@/core/api';

export function Topbar() {
  const { wsStatus, bots, unreadAlerts, markAlertsRead, alerts } = useAppStore();
  const navigate = useNavigate();
  const [showAlerts, setShowAlerts] = useState(false);
  const alertRef = useRef<HTMLDivElement>(null);

  const activeBots = bots.filter(b => b.status === 'running');
  const activeSymbols = activeBots.map(b => b.symbol);

  const handleLogout = () => {
    clearApiKey();
    navigate('/login');
  };

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (alertRef.current && !alertRef.current.contains(e.target as Node)) setShowAlerts(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-border bg-card shrink-0 z-50">
      {/* Left */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-accent" />
          <span className="font-semibold text-sm tracking-tight">OmniTrader</span>
        </div>
      </div>

      {/* Center — Asset Picker */}
      <div className="hidden md:flex items-center gap-2">
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-border bg-secondary/50 hover:bg-secondary text-xs transition-colors">
          <span className="text-muted-foreground">Active:</span>
          <span className="font-medium">
            {activeSymbols.length > 0 ? activeSymbols.slice(0, 3).join(', ') : 'No active symbols'}
          </span>
          {activeSymbols.length > 3 && (
            <StatusBadge variant="info" size="sm">+{activeSymbols.length - 3}</StatusBadge>
          )}
          <ChevronDown className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">
        <StatusBadge variant="warning" size="sm">Paper</StatusBadge>

        <div className="flex items-center gap-1" title={`WebSocket: ${wsStatus}`}>
          {wsStatus === 'connected'
            ? <Wifi className="h-3.5 w-3.5 text-success" />
            : <WifiOff className="h-3.5 w-3.5 text-danger" />
          }
        </div>

        {/* Alerts bell */}
        <div className="relative" ref={alertRef}>
          <button
            onClick={() => { setShowAlerts(!showAlerts); markAlertsRead(); }}
            className="relative p-1.5 rounded-md hover:bg-secondary transition-colors"
          >
            <Bell className="h-4 w-4 text-muted-foreground" />
            {unreadAlerts > 0 && (
              <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-danger text-[10px] font-bold flex items-center justify-center text-foreground">
                {unreadAlerts}
              </span>
            )}
          </button>

          {showAlerts && (
            <div className="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto rounded-lg border border-border bg-card shadow-xl z-50">
              <div className="p-3 border-b border-border">
                <h4 className="text-xs font-semibold">Alerts</h4>
              </div>
              {alerts.length === 0 ? (
                <div className="px-3 py-4 text-[11px] text-muted-foreground">No live alerts yet.</div>
              ) : (
                alerts.map((a, i) => (
                  <div key={i} className="px-3 py-2.5 border-b border-border/50 hover:bg-secondary/30 last:border-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <StatusBadge
                        variant={a.level === 'critical' ? 'danger' : a.level === 'warning' ? 'warning' : 'info'}
                        size="sm"
                      >
                        {a.level}
                      </StatusBadge>
                      <span className="text-xs font-medium">{a.title}</span>
                    </div>
                    <p className="text-[11px] text-muted-foreground">{a.body}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <Link to="/settings" className="p-1.5 rounded-md hover:bg-secondary transition-colors">
          <Settings className="h-4 w-4 text-muted-foreground" />
        </Link>

        <button onClick={handleLogout} className="p-1.5 rounded-md hover:bg-secondary transition-colors" title="Logout">
          <LogOut className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>
    </header>
  );
}
