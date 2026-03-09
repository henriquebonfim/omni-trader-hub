import { Panel } from '@/components/shared/Panel';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { ProgressBar } from '@/components/shared/ProgressBar';
import { mockCircuitBreakers } from '@/lib/mock-data';
import { CycleMessage } from '@/lib/ws';

interface RiskMonitorProps {
  data: CycleMessage;
}

export default function RiskMonitor({ data }: RiskMonitorProps) {
  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">🛡️ Risk Monitor</h1>

      {/* Circuit Breakers */}
      <Panel title="Circuit Breakers">
        <div className="space-y-3">
          {mockCircuitBreakers.map((cb) => (
            <div key={cb.name} className="p-3 rounded-lg bg-muted">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-foreground font-medium">{cb.name}</span>
                  <span className="text-xs text-muted-foreground">Limit: {cb.limit}{cb.name.includes('Loss') ? '%' : ''}</span>
                </div>
                <StatusBadge variant={cb.status === 'ok' ? 'success' : cb.status === 'warn' ? 'warning' : 'danger'}>
                  {cb.status === 'ok' ? '✅ OK' : cb.status === 'warn' ? '⚠️ WARN' : '🔴 TRIGGERED'}
                </StatusBadge>
              </div>
              <ProgressBar value={Math.abs(cb.current)} max={Math.abs(cb.limit)} variant="auto" showLabel />
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Position Risk */}
        <Panel title="Position Risk">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Notional Exposure</span><span className="font-mono text-foreground">$1,003.35 (9.2%)</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Max Position Size</span><span className="font-mono text-foreground">$218.00 (2.0%)</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Current Leverage</span><span className="font-mono text-foreground">3.0×</span></div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Liquidation Price</span>
              <div className="flex items-center gap-2">
                <span className="font-mono text-foreground">$44,593.00</span>
                <StatusBadge variant="success">34% away</StatusBadge>
              </div>
            </div>
            <div className="flex justify-between"><span className="text-muted-foreground">SL Risk</span><span className="font-mono text-trading-red">-$139.00</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">TP Target</span><span className="font-mono text-trading-green">+$231.00</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Risk/Reward</span><span className="font-mono text-primary">1:1.66</span></div>
          </div>
        </Panel>

        {/* Drawdown Tracker */}
        <Panel title="Drawdown Tracker">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Peak Equity</span><span className="font-mono text-foreground">$11,052.80 (Mar 5)</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Current Equity</span><span className="font-mono text-foreground">${data.balance.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Drawdown</span><span className="font-mono text-trading-red">-$205.48 (-1.91%)</span></div>
            <div className="mt-2">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>-1.91%</span><span>Trigger: -10%</span>
              </div>
              <ProgressBar value={1.91} max={10} variant="auto" />
            </div>
            <div className="flex justify-between mt-2">
              <span className="text-muted-foreground">Auto-Deleverage</span>
              <StatusBadge variant="neutral">Inactive (triggers at -8%)</StatusBadge>
            </div>
          </div>
        </Panel>
      </div>

      {/* Streak Tracking */}
      <Panel title="Streak Tracking">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-muted text-center">
            <p className="text-xs text-muted-foreground">Current Streak</p>
            <p className="text-xl font-bold text-trading-green mt-1">W3</p>
          </div>
          <div className="p-3 rounded-lg bg-muted text-center">
            <p className="text-xs text-muted-foreground">Best Win Streak</p>
            <p className="text-xl font-bold text-foreground mt-1">W8</p>
          </div>
          <div className="p-3 rounded-lg bg-muted text-center">
            <p className="text-xs text-muted-foreground">Worst Loss Streak</p>
            <p className="text-xl font-bold text-foreground mt-1">L4</p>
          </div>
          <div className="p-3 rounded-lg bg-muted text-center">
            <p className="text-xs text-muted-foreground">Size Multiplier</p>
            <p className="text-xl font-bold text-trading-green mt-1">1.0×</p>
          </div>
        </div>
      </Panel>
    </div>
  );
}
