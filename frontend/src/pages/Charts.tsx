import { cn } from '@/core/utils';
import { fetchMarkets } from '@/domains/market/api';
import type { MarketPair } from '@/domains/market/types';
import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { CandlestickSeries, ColorType, createChart, HistogramSeries, UTCTimestamp } from 'lightweight-charts';
import { Maximize2, Minimize2 } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

interface CandleData {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface VolumeData {
  time: UTCTimestamp;
  value: number;
  color: string;
}

interface BackendCandle {
  time: number; // unix seconds (float) from backend
  open: number;
  high: number;
  low: number;
  close: number;
  value?: number;
}

function sma(values: number[], period: number): number {
  const window = values.slice(-period);
  if (window.length === 0) return 0;
  return window.reduce((sum, value) => sum + value, 0) / window.length;
}

function ema(values: number[], period: number): number {
  if (values.length === 0) return 0;
  const k = 2 / (period + 1);
  let current = values[0];
  for (let i = 1; i < values.length; i += 1) {
    current = values[i] * k + current * (1 - k);
  }
  return current;
}

function std(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const variance = values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}

function generateVolumeData(candleData: CandleData[]): VolumeData[] {
  return candleData.map((c) => ({
    time: c.time,
    value: c.volume,
    color: c.close >= c.open ? 'rgba(63, 185, 80, 0.3)' : 'rgba(248, 81, 73, 0.3)',
  }));
}

import { request } from '@/core/api';

export default function Charts() {
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('1h');
  const [fullscreen, setFullscreen] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [candles, setCandles] = useState<CandleData[]>([]);
  const [markets, setMarkets] = useState<MarketPair[]>([]);
  const [candlesError, setCandlesError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarkets().then(setMarkets).catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedSymbol) {
      setCandles([]);
      setCandlesError(null);
      return;
    }
    request<{ ok: boolean; data: BackendCandle[]; message?: string }>(`/api/candles/?symbol=${encodeURIComponent(selectedSymbol)}&timeframe=${timeframe}&limit=200`)
      .then((res) => {
        if (!res?.ok) {
          setCandles([]);
          setCandlesError(res?.message || 'Unable to load candles');
          return;
        }
        const adapted: CandleData[] = (res.data || []).map((c) => ({
          time: c.time as UTCTimestamp,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
          volume: c.value ?? 0,
        }));
        setCandles(adapted);
        setCandlesError(adapted.length === 0 ? 'No candle data available.' : null);
      })
      .catch((e) => {
        console.error(e);
        setCandles([]);
        setCandlesError('Failed to load candles.');
      });
  }, [selectedSymbol, timeframe]);

  const symbolOptions = markets.map((market) => market.symbol);
  const candleData = candles;
  const volumeData = useMemo(() => generateVolumeData(candleData), [candleData]);
  const closeSeries = useMemo(() => candleData.map((candle) => candle.close), [candleData]);
  const highSeries = useMemo(() => candleData.map((candle) => candle.high), [candleData]);
  const lowSeries = useMemo(() => candleData.map((candle) => candle.low), [candleData]);
  const latestClose = closeSeries.length > 0 ? closeSeries[closeSeries.length - 1] : 0;

  const ema9 = useMemo(() => ema(closeSeries, 9), [closeSeries]);
  const ema21 = useMemo(() => ema(closeSeries, 21), [closeSeries]);
  const sma50 = useMemo(() => sma(closeSeries, 50), [closeSeries]);
  const recentWindow = useMemo(() => closeSeries.slice(-14), [closeSeries]);
  const bbMid = useMemo(() => sma(recentWindow, recentWindow.length || 1), [recentWindow]);
  const bbStd = useMemo(() => std(recentWindow), [recentWindow]);
  const bbUpper = bbMid + 2 * bbStd;
  const bbLower = bbMid - 2 * bbStd;
  const atr14 = useMemo(() => {
    const ranges = candleData.slice(-14).map((c) => c.high - c.low);
    return ranges.length > 0 ? ranges.reduce((sum, value) => sum + value, 0) / ranges.length : 0;
  }, [candleData]);
  const momentumPct = useMemo(() => {
    if (closeSeries.length < 15) return 0;
    const base = closeSeries[closeSeries.length - 15];
    if (!base) return 0;
    return ((latestClose - base) / base) * 100;
  }, [closeSeries, latestClose]);
  const volatilityPct = latestClose > 0 ? (atr14 / latestClose) * 100 : 0;
  const regimeConfidence = Math.min(95, Math.round(Math.abs(momentumPct) * 4 + volatilityPct * 6));
  const regime = volatilityPct > 2 ? 'VOLATILE' : Math.abs(momentumPct) > 1.5 ? 'TRENDING' : 'RANGING';
  const regimeBadge: 'success' | 'warning' | 'info' = regime === 'TRENDING' ? 'success' : regime === 'VOLATILE' ? 'warning' : 'info';
  const bias = momentumPct >= 0 ? 'BULLISH' : 'BEARISH';
  const avgVolume = useMemo(() => {
    const recent = volumeData.slice(-20);
    if (recent.length === 0) return 0;
    return recent.reduce((sum, v) => sum + v.value, 0) / recent.length;
  }, [volumeData]);
  const indicatorTiles = [
    ['EMA(9)', ema9],
    ['EMA(21)', ema21],
    ['SMA(50)', sma50],
    ['BB Upper', bbUpper],
    ['BB Mid', bbMid],
    ['BB Lower', bbLower],
    ['ATR(14)', atr14],
    ['Momentum 14', momentumPct],
    ['Volatility', volatilityPct],
    ['Volume Avg', avgVolume],
    ['Last Close', latestClose],
    ['Range', highSeries.length > 0 && lowSeries.length > 0 ? highSeries[highSeries.length - 1] - lowSeries[lowSeries.length - 1] : 0],
  ];

  useEffect(() => {
    if (!selectedSymbol && symbolOptions.length > 0) {
      setSelectedSymbol(symbolOptions[0]);
    }
  }, [selectedSymbol, symbolOptions]);

  useEffect(() => {
    if (!chartContainerRef.current || candleData.length === 0) return;
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
  }, [candleData, volumeData]);

  return (
    <div className={cn('space-y-4 animate-fade-in', fullscreen && 'fixed inset-0 z-50 bg-background p-4')}>
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Charts</h1>
        <div className="flex items-center gap-2">
          <select
            value={selectedSymbol}
            onChange={e => setSelectedSymbol(e.target.value)}
            disabled={symbolOptions.length === 0}
            className="px-2 py-1.5 rounded-md border border-border bg-secondary/30 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {symbolOptions.length === 0 && <option value="">No markets</option>}
            {symbolOptions.map(symbol => (
              <option key={symbol} value={symbol}>{symbol}</option>
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
        {candlesError ? (
          <div className="h-full flex items-center justify-center text-sm text-muted-foreground">{candlesError}</div>
        ) : candleData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sm text-muted-foreground">Loading candles...</div>
        ) : (
          <div ref={chartContainerRef} className="w-full h-full" />
        )}
      </div>

      {/* Indicators & Regime */}
      {!fullscreen && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Panel title="Indicators" subtitle={selectedSymbol}>
            <div className="grid grid-cols-3 gap-2 text-xs">
              {indicatorTiles.map(([label, val]) => (
                <div key={label} className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">{label}</span>
                  <p className="font-mono font-medium text-[11px]">
                    {label === 'Momentum 14' || label === 'Volatility' ? `${(val as number).toFixed(2)}%` : (val as number).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Regime Detection">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <StatusBadge variant={regimeBadge} size="md" pulse>{regime}{regime === 'TRENDING' ? ' ▲' : regime === 'VOLATILE' ? ' ⚠' : ' ▬'}</StatusBadge>
                <span className="text-xs text-muted-foreground">Confidence: {regimeConfidence}%</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">Momentum (14)</span>
                  <p className="font-mono font-medium">{momentumPct.toFixed(2)}%</p>
                </div>
                <div className="rounded border border-border/50 p-2 bg-secondary/20">
                  <span className="text-muted-foreground text-[10px]">ATR (14)</span>
                  <p className="font-mono font-medium">{atr14.toFixed(2)}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Bias:</span>
                <StatusBadge variant={momentumPct >= 0 ? 'success' : 'danger'} size="sm">{bias} {momentumPct >= 0 ? '↑' : '↓'}</StatusBadge>
              </div>
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
}
