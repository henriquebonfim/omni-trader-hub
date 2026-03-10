import { StatusBadge } from '@/core/shared/StatusBadge';
import { Circle, Wifi, WifiOff } from 'lucide-react';

interface TopBarProps {
  wsStatus: 'connecting' | 'open' | 'closed';
  botRunning?: boolean;
}

export function TopBar({ wsStatus, botRunning = true }: TopBarProps) {
  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-border bg-card shrink-0">
      <div className="flex items-center gap-3">
        <Circle className={`h-3 w-3 fill-current ${botRunning ? 'text-trading-green' : 'text-trading-red'}`} />
        <span className="font-bold text-foreground tracking-tight">Omni-Trader Hub</span>
      </div>

      <div className="hidden md:flex items-center gap-3">
        <span className="text-sm font-semibold text-foreground">BTC/USDT</span>
        <StatusBadge variant="warning">Paper</StatusBadge>
        <span className="text-xs text-muted-foreground">ADX Trend + Bollinger</span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          {wsStatus === 'open' ? (
            <Wifi className="h-4 w-4 text-trading-green" />
          ) : (
            <WifiOff className="h-4 w-4 text-trading-red" />
          )}
          <span className={`text-xs ${wsStatus === 'open' ? 'text-trading-green' : 'text-trading-red'}`}>
            {wsStatus === 'open' ? 'Connected' : wsStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>
        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
          AT
        </div>
      </div>
    </header>
  );
}
