import { Panel } from '@/core/shared/Panel';
import { StatusBadge } from '@/core/shared/StatusBadge';
import { StatCard } from '@/core/shared/StatCard';
import { Button } from '@/core/ui/button';
import { CycleMessage } from '@/core/api/ws';

interface TradeExecutionProps {
  data: CycleMessage;
}

export default function TradeExecution({ data }: TradeExecutionProps) {
  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">⚙️ Trade Execution</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Current Position */}
        <Panel title="Current Position">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <StatusBadge variant={data.position === 'long' ? 'success' : data.position === 'short' ? 'danger' : 'neutral'} size="md">
                {(data.position ?? 'FLAT').toUpperCase()}
              </StatusBadge>
              <span className="text-sm text-muted-foreground">BTC/USDT</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Entry Price</span><span className="font-mono text-foreground">$66,890.00</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Size</span><span className="font-mono text-foreground">0.015 BTC</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Notional</span><span className="font-mono text-foreground">$1,003.35</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Unrealized P&L</span><span className="font-mono text-trading-green">+$42.15</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Time Open</span><span className="font-mono text-foreground">2h 14m</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Stop Loss</span><span className="font-mono text-trading-red">$65,500.00</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Take Profit</span><span className="font-mono text-trading-green">$69,200.00</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Trailing Stop</span><StatusBadge variant="success">Active</StatusBadge></div>
            </div>
            <Button variant="outline" className="w-full border-trading-red/30 text-trading-red hover:bg-trading-red/10">
              Close Position
            </Button>
          </div>
        </Panel>

        {/* Manual Trade Controls */}
        <Panel title="Manual Trade Controls">
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-2">
              <Button className="bg-trading-green/20 text-trading-green border border-trading-green/30 hover:bg-trading-green/30" variant="outline">
                MARKET LONG
              </Button>
              <Button className="bg-trading-red/20 text-trading-red border border-trading-red/30 hover:bg-trading-red/30" variant="outline">
                MARKET SHORT
              </Button>
              <Button variant="outline" className="border-trading-yellow/30 text-trading-yellow hover:bg-trading-yellow/10">
                CLOSE ALL
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Position Size (%)</label>
                <input type="number" defaultValue={2.0} step={0.1} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Leverage</label>
                <select defaultValue="3" className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground">
                  <option value="1">1×</option><option value="2">2×</option><option value="3">3×</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Stop Loss ($)</label>
                <input type="number" defaultValue={65500} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">Take Profit ($)</label>
                <input type="number" defaultValue={69200} className="w-full bg-muted border border-border rounded-md px-3 py-2 text-sm text-foreground" />
              </div>
            </div>
            <div className="p-2 rounded bg-muted text-xs text-muted-foreground">
              Risk: <span className="text-trading-red font-mono">$139.00</span> at stop loss
            </div>
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Exchange Adapter */}
        <Panel title="Exchange Adapter Status">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-trading-green" />
              <span className="text-sm text-foreground font-medium">Active: Binance Direct</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-muted-foreground" />
              <span className="text-sm text-muted-foreground">Fallback: CCXT (Available)</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <StatCard label="Success Rate" value="99.8" suffix="%" variant="green" />
              <StatCard label="Avg Latency" value="45" suffix="ms" variant="accent" />
              <StatCard label="Errors (24h)" value={2} variant="default" />
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="text-xs">Test Connection</Button>
              <Button variant="outline" size="sm" className="text-xs">Switch Adapter</Button>
            </div>
          </div>
        </Panel>

        {/* Execution Quality */}
        <Panel title="Execution Quality">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <StatCard label="Avg Slippage" value="0.032" suffix="%" />
              <StatCard label="Fill Rate" value="94.5" suffix="%" variant="green" />
              <StatCard label="Maker Rebate" value="$12.45" variant="accent" />
              <StatCard label="Order Type" value="Market" />
            </div>
            <div className="p-3 rounded-lg bg-trading-yellow/10 border border-trading-yellow/20 text-xs text-trading-yellow">
              💡 Consider limit orders to reduce slippage. Potential savings: ~$8.20/week
            </div>
          </div>
        </Panel>
      </div>

      {/* Semi-Auto Queue Placeholder */}
      <Panel title="Signal Approval Queue">
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <span className="text-3xl mb-2">📭</span>
          <p className="text-sm text-foreground font-medium">No pending signals</p>
          <p className="text-xs text-muted-foreground mt-1">Signals will appear here in semi-auto mode</p>
        </div>
      </Panel>
    </div>
  );
}
