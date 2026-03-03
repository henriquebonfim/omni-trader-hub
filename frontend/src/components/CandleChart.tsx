import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time, CandlestickSeries } from 'lightweight-charts';

interface CandleChartProps {
  symbol?: string;
}

const TIMEFRAMES = [
  '1 sec', '10 sec', '30 sec',
  '1 min', '5 min', '15 min', '30 min',
  '1 hour', '3 hours', '12 hours',
  '1D', '3D', '5D', '7D', '15D',
  '1Y', '3Y', '5Y', '7Y', '9Y'
];

export default function CandleChart({ symbol }: CandleChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const [timeframe, setTimeframe] = useState('15 min');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    chartRef.current = chart;
    seriesRef.current = candleSeries;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    const fetchCandles = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/candles?timeframe=${encodeURIComponent(timeframe)}`);
        const json = await res.json();
        if (json.ok && seriesRef.current) {
          if (json.data && json.data.length > 0) {
              seriesRef.current.setData(json.data as CandlestickData<Time>[]);
          } else {
              setError("No data returned for this timeframe.");
              seriesRef.current.setData([]);
          }
        } else {
            setError(json.message || "Failed to fetch candles");
        }
      } catch (err) {
        console.error("Failed to fetch candles", err);
        setError("Network error");
      } finally {
        setLoading(false);
      }
    };

    fetchCandles();
  }, [timeframe]);

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ marginBottom: 0 }}>Chart {symbol && `- ${symbol}`}</h2>
        <select 
          value={timeframe} 
          onChange={(e) => setTimeframe(e.target.value)}
          style={{ background: 'var(--bg-lighter)', color: 'var(--text)', border: '1px solid var(--border)', padding: '4px 8px', borderRadius: '4px' }}
        >
          {TIMEFRAMES.map(tf => (
            <option key={tf} value={tf}>{tf}</option>
          ))}
        </select>
      </div>
      {loading && <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading chart data...</div>}
      {error && <div style={{ textAlign: 'center', color: 'var(--red)' }}>{error}</div>}
      <div ref={chartContainerRef} style={{ width: '100%', height: '400px', display: (loading || error) ? 'none' : 'block' }} />
    </div>
  );
}
