import { useEffect, useRef, useState } from 'react';
import { Panel } from '@/components/shared/Panel';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { mockBots, mockPrices } from '@/lib/mock-data';
import { cn } from '@/lib/utils';
import { createChart, ColorType, CandlestickSeries, HistogramSeries } from 'lightweight-charts';
import { Maximize2, Minimize2 } from 'lucide-react';

function generateCandleData(basePrice: number, count: number) {
  const data = [];
  let price = basePrice;
  const now = Math.floor(Date.now() / 1000);
  for (let i = count; i >= 0; i--) {
    const time = now - i * 3600;
    const open = price;
    const high = open + Math.random() * open * 0.015;
    const low = open - Math.random() * open * 0.015;
    const close = low + Math.random() * (high - low);
    price = close;
    data.push({
      time: time as any,
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
    });
  }
  return data;
}

function generateVolumeData(candleData: any[]) {
  return candleData.map((c: any) => ({
    time: c.time,
    value: Math.random() * 1000000 + 500000,
    color: c.close >= c.open ? 'rgba(63, 185, 80, 0.3)' : 'rgba(248, 81, 73, 0.3)',
  }));
}

export default function Charts() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [fullscreen, setFullscreen] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const basePrice = mockPrices[selectedSymbol] || 67000;
  const candleData = generateCandleData(basePrice * 0.95, 200);
  const volumeData = generateVolumeData(candleData);

  useEffect(() => {
    if (!chartContainerRef.current) return;
    const container = chartContainerRef.current;
    container.innerHTML = '';

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#8b949e',
        fontFamily: 'Inter',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(48, 54, 61, 0.5)' },
        horzLines: { color: 'rgba(48, 54, 61, 0.5)' },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: '#30363d' },
      timeScale: { borderColor: '#30363d', timeVisible: true },
      width: container.clientWidth,
      height: container.clientHeight,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#3fb950',
      downColor: '#f85149',
      borderDownColor: '#f85149',
      borderUpColor: '#3fb950',
      wickDownColor: '#f85149',
      wickUpColor: '#3fb950',
    });
    candleSeries.setData(candleData);

    const volSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    volSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    volSeries.setData(volumeData);

    chart.timeScale().fitContent();

    const handleResize = () => {
      chart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, [selectedSymbol, timeframe, fullscreen]);

  return (
    <div className={cn('space-y-4 animate-fade-in', fullscreen && 'fixed inset-0 z-50 bg-background p-4')}>
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Charts</h1>
        <div className="flex items-center gap-2">
          <select
            value={selectedSymbol}
            onChange={e => setSelectedSymbol(e.target.value)}
            className="px-2 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {mockBots.map(b => (
              <option key={b.symbol} value={b.symbol}>{b.symbol}</option>
            ))}
          </select>

          <div className="flex border border-border rounded-md overflow-hidden">
            {['5m', '15m', '1h', '4h', '1d'].map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={cn(
                  'px-2.5 py-1 text-[11px] font-medium transition-colors',
                  timeframe === tf ? 'bg-accent/15 text-accent' : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                )}
              >
                {tf}
              </button>
            ))}
          </div>

          <button onClick={() => setFullscreen(!fullscreen)} className="p-1.5 rounded hover:bg-secondary transition-colors">
            {fullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div className={cn('rounded-lg border border-border bg-card', fullscreen ? 'flex-1 h-[calc(100vh-120px)]' : 'h-[500px]')}>
        <div ref={chartContainerRef} className="w-full h-full" />
      </div>

      {/* Indicators & Regime */}
      {!fullscreen && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Panel title="Indicators" subtitle={selectedSymbol}>
            <div className="grid grid-cols-3 gap-2 text-xs">
              {[
                ['EMA(9)', '67,412'], ['EMA(21)', '66,890'], ['SMA(50)', '65,200'],
                ['RSI(14)', '58.3'], ['MACD', '+125.4'], ['Stochastic', '72.1'],
                ['BB Upper', '68,900'], ['BB Mid', '67,100'], ['BB Lower', '65,300'],
                ['ATR(14)', '842'], ['ADX', '32.5'], ['Volume', '1.2M'],
              ].map(([label, val]) => (
                <div key={label} className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">{label}</span>
                  <p className="font-mono font-medium text-[11px]">{val}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Regime Detection">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <StatusBadge variant="success" size="md" pulse>TRENDING ▲</StatusBadge>
                <span className="text-xs text-muted-foreground">Confidence: 78%</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">ADX</span>
                  <p className="font-mono font-medium">32.5</p>
                </div>
                <div className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">ATR</span>
                  <p className="font-mono font-medium">842</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Bias:</span>
                <StatusBadge variant="success" size="sm">BULLISH ↑</StatusBadge>
              </div>
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
}
