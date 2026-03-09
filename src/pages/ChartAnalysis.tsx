import { Panel } from '@/components/shared/Panel';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, HistogramSeries, type IChartApi } from 'lightweight-charts';

function generateCandleData(count: number) {
  const data = [];
  let open = 67000;
  const baseTime = Math.floor(Date.now() / 1000) - count * 3600;
  for (let i = 0; i < count; i++) {
    const close = open + (Math.random() - 0.48) * 400;
    const high = Math.max(open, close) + Math.random() * 200;
    const low = Math.min(open, close) - Math.random() * 200;
    data.push({
      time: (baseTime + i * 3600) as any,
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
    });
    open = close;
  }
  return data;
}

function generateVolumeData(candleData: any[]) {
  return candleData.map((c) => ({
    time: c.time,
    value: Math.random() * 1000 + 200,
    color: c.close >= c.open ? 'rgba(63, 185, 80, 0.3)' : 'rgba(248, 81, 73, 0.3)',
  }));
}

export default function ChartAnalysis() {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<IChartApi | null>(null);
  const [timeframe, setTimeframe] = useState<'15m' | '1h' | '4h' | '1d'>('1h');

  useEffect(() => {
    if (!chartRef.current) return;

    // Clear previous
    if (chartInstance.current) {
      chartInstance.current.remove();
    }

    const chart = createChart(chartRef.current, {
      layout: { background: { color: 'transparent' }, textColor: 'hsl(215, 10%, 55%)' },
      grid: { vertLines: { color: 'hsl(215, 14%, 18%)' }, horzLines: { color: 'hsl(215, 14%, 18%)' } },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: 'hsl(215, 14%, 22%)' },
      timeScale: { borderColor: 'hsl(215, 14%, 22%)' },
      width: chartRef.current.clientWidth,
      height: 400,
    });
    chartInstance.current = chart;

    const counts = { '15m': 96, '1h': 168, '4h': 90, '1d': 60 };
    const candleData = generateCandleData(counts[timeframe]);

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: 'hsl(140, 60%, 52%)',
      downColor: 'hsl(2, 93%, 63%)',
      borderUpColor: 'hsl(140, 60%, 52%)',
      borderDownColor: 'hsl(2, 93%, 63%)',
      wickUpColor: 'hsl(140, 60%, 52%)',
      wickDownColor: 'hsl(2, 93%, 63%)',
    });
    candleSeries.setData(candleData);

    const volumeSeries = chart.addSeries(VolumeSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
    volumeSeries.setData(generateVolumeData(candleData));

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartRef.current) chart.applyOptions({ width: chartRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartInstance.current = null;
    };
  }, [timeframe]);

  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">📈 Chart Analysis</h1>

      <Panel
        title="BTC/USDT"
        actions={
          <div className="flex gap-1">
            {(['15m', '1h', '4h', '1d'] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2 py-1 text-xs rounded ${timeframe === tf ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
              >
                {tf}
              </button>
            ))}
          </div>
        }
      >
        <div ref={chartRef} className="w-full" />
      </Panel>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Panel title="Indicators">
          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              ['EMA(9)', '67,245.30'],
              ['EMA(21)', '66,890.15'],
              ['RSI(14)', '62.4'],
              ['BB Upper', '68,120.00'],
              ['BB Lower', '65,800.00'],
              ['ATR(14)', '1,245.50'],
              ['ADX', '28.7'],
            ].map(([label, val]) => (
              <div key={label} className="flex justify-between p-2 rounded bg-muted">
                <span className="text-muted-foreground">{label}</span>
                <span className="font-mono text-foreground">{val}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Regime Analysis">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <StatusBadge variant="success" size="md">TRENDING ▲</StatusBadge>
              <StatusBadge variant="info" size="md">BULLISH ↑</StatusBadge>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">ADX</span><span className="text-foreground font-mono">28.7 (Strong)</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">ATR</span><span className="text-foreground font-mono">1,245.50</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Confidence</span><span className="text-foreground font-mono">78%</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Volatility</span><span className="text-trading-yellow font-mono">Medium</span></div>
            </div>
            <div className="p-3 rounded-lg bg-muted border border-border">
              <p className="text-xs text-muted-foreground mb-1">SMC Analysis</p>
              <StatusBadge variant="neutral">Coming Soon</StatusBadge>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
