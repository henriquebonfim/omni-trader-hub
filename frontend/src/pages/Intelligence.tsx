import { cn } from '@/core/utils';
import { fetchCorrelationMatrix, fetchCrisisStatus, fetchMacroIndicators, fetchNews, fetchSentiment, toggleCrisisMode } from '@/domains/market/api';
import type { CorrelationMatrixData, NewsItem, SentimentData } from '@/domains/market/types';
import type { CrisisStatus } from '@/domains/system/types';
import { CorrelationHeatmap } from '@/shared/ui/organisms/CorrelationHeatmap';
import { EmptyState } from '@/shared/ui/molecules/EmptyState';
import { Panel } from '@/shared/ui/molecules/Panel';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { AlertCircle, AlertTriangle, Loader2, Newspaper, TrendingDown, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { AIOverviewCard } from '@/features/intelligence/AIOverview';

export default function Intelligence() {
  const [newsFilter, setNewsFilter] = useState<'all' | 'high' | 'asset'>('all');
  const [selectedAsset, setSelectedAsset] = useState<string>('BTC/USDT');
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [crisisStatus, setCrisisStatus] = useState<CrisisStatus | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [correlationData, setCorrelationData] = useState<CorrelationMatrixData | null>(null);
  const [fearGreed, setFearGreed] = useState<number | null>(null);

  const [loadingSentiment, setLoadingSentiment] = useState(true);
  const [errorSentiment, setErrorSentiment] = useState(false);

  const [loadingCrisis, setLoadingCrisis] = useState(true);
  const [errorCrisis, setErrorCrisis] = useState(false);

  const [loadingNews, setLoadingNews] = useState(true);
  const [errorNews, setErrorNews] = useState(false);

  const [loadingCorrelation, setLoadingCorrelation] = useState(true);
  const [errorCorrelation, setErrorCorrelation] = useState(false);

  useEffect(() => {
    fetchSentiment('BTC/USDT')
      .then(res => { setSentimentData(res); setErrorSentiment(false); })
      .catch(e => { console.error(e); setErrorSentiment(true); })
      .finally(() => setLoadingSentiment(false));

    fetchCrisisStatus()
      .then(res => { setCrisisStatus(res); setErrorCrisis(false); })
      .catch(e => { console.error(e); setErrorCrisis(true); })
      .finally(() => setLoadingCrisis(false));

    fetchNews()
      .then(res => { if (res) setNews(res); setErrorNews(false); })
      .catch(e => { console.error(e); setErrorNews(true); })
      .finally(() => setLoadingNews(false));

    fetchCorrelationMatrix({ timeframe: '1h', limit: 120 })
      .then(res => { setCorrelationData(res); setErrorCorrelation(false); })
      .catch(e => { console.error(e); setErrorCorrelation(true); })
      .finally(() => setLoadingCorrelation(false));

    fetchMacroIndicators()
      .then((rows) => {
        const fg = rows.find(r => r.name === 'Fear & Greed Index');
        setFearGreed(fg ? fg.value : null);
      })
      .catch(console.error);
  }, []);

  const sentiment = sentimentData?.score || 0;
  const crisisActive = crisisStatus?.active || false;
  const fearGreedValue = fearGreed ?? 62;
  const fearGreedLabel = fearGreedValue > 70 ? 'Extreme Greed' : fearGreedValue > 55 ? 'Greed' : fearGreedValue > 45 ? 'Neutral' : fearGreedValue > 30 ? 'Fear' : 'Extreme Fear';
  const divergenceDetected = Math.abs(sentiment) >= 0.5;

  const allAssets = Array.from(new Set(news.flatMap((item) => item.assets))).sort();
  const filteredNews = newsFilter === 'high'
    ? news.filter(n => n.impact_level > 0.7)
    : newsFilter === 'asset'
      ? news.filter((n) => n.assets.includes(selectedAsset))
      : news;

  const sentimentLabel = sentiment > 0.5 ? 'Bullish' : sentiment > 0.2 ? 'Slightly Bullish' : sentiment > -0.2 ? 'Neutral' : sentiment > -0.5 ? 'Slightly Bearish' : 'Bearish';
  const sentimentEmoji = sentiment > 0.5 ? '😊' : sentiment > 0.2 ? '🙂' : sentiment > -0.2 ? '😐' : sentiment > -0.5 ? '😟' : '😢';

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Intelligence</h1>

      {/* Top row */}
      <div className="grid grid-cols-1 gap-4">
        <AIOverviewCard />
      </div>

      {/* Divergence alert banner */}
      {divergenceDetected && (
        <div className="rounded-md border border-warning/30 bg-warning/5 p-3 flex items-center gap-3">
          <AlertTriangle className="h-4 w-4 text-warning shrink-0" />
          <div>
            <p className="text-xs font-medium text-warning">Divergence Detected</p>
            <p className="text-[11px] text-muted-foreground">Sentiment is at {sentiment.toFixed(2)} on BTC/USDT. Monitor position sizing and drawdown closely.</p>
          </div>
        </div>
      )}

      <Panel title="Cross-Asset Correlation" subtitle="Rolling return relationships across active symbols">
        {loadingCorrelation ? (
          <div className="flex items-center justify-center py-10">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : errorCorrelation || !correlationData ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground py-1">
            <AlertCircle className="h-4 w-4 text-warning" />
            <span>Correlation matrix unavailable right now.</span>
          </div>
        ) : (
          <CorrelationHeatmap data={correlationData} compact />
        )}
      </Panel>

      {/* News Feed */}
      <Panel
        title="News Feed"
        actions={
          <div className="flex gap-1 items-center">
            {(['all', 'high', 'asset'] as const).map(f => (
              <button
                key={f}
                onClick={() => setNewsFilter(f)}
                disabled={loadingNews || errorNews}
                className={cn(
                  'px-2 py-0.5 rounded text-[11px] transition-colors capitalize',
                  newsFilter === f ? 'bg-accent/15 text-accent' : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {f === 'high' ? 'High Impact' : f === 'asset' ? 'By Asset' : 'All'}
              </button>
            ))}
            {newsFilter === 'asset' && (
              <select
                value={selectedAsset}
                onChange={(e) => setSelectedAsset(e.target.value)}
                className="px-2 py-0.5 rounded border border-border bg-secondary/30 text-[11px] focus:outline-none focus:ring-1 focus:ring-accent"
              >
                {allAssets.length === 0 ? (
                  <option value="">No assets</option>
                ) : (
                  allAssets.map((asset) => (
                    <option key={asset} value={asset}>{asset}</option>
                  ))
                )}
              </select>
            )}
          </div>
        }
      >
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {loadingNews ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : errorNews ? (
            <EmptyState
              icon={AlertCircle}
              title="News feed unavailable"
              description="Could not connect to the intelligence server."
            />
          ) : filteredNews.length === 0 ? (
            <EmptyState
              icon={Newspaper}
              title="No news found"
              description="There are no recent articles matching your filter."
            />
          ) : (
            filteredNews.map(item => (
              <div key={item.id} className="flex items-start gap-3 p-3 rounded-md border border-border/50 hover:bg-secondary/30 transition-colors">
                <Newspaper className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium leading-snug">{item.title}</p>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    <span className="text-[10px] text-muted-foreground">{item.source}</span>
                    <StatusBadge
                      variant={item.impact_level > 0.7 ? 'danger' : item.impact_level > 0.4 ? 'warning' : 'info'}
                      size="sm"
                    >
                      {item.impact_level > 0.7 ? '🔴 HIGH' : item.impact_level > 0.4 ? '🟡 MED' : '🔵 LOW'}
                    </StatusBadge>
                    <span className="text-[10px]">
                      {item.sentiment_score > 0 ? '🙂' : item.sentiment_score < 0 ? '😟' : '😐'} {item.sentiment_score.toFixed(2)}
                    </span>
                    {item.assets.map((a, idx) => (
                      <span key={`${item.id}-${a}-${idx}`}>
                        <StatusBadge variant="neutral" size="sm">{a}</StatusBadge>
                      </span>
                    ))}
                    <span className="text-[10px] text-muted-foreground ml-auto">
                      {Math.floor((Date.now() - item.published_at) / 3600000)}h ago
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Panel>
    </div>
  );
}

function MacroRow({ label, value, change }: { label: string; value: string; change: number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-xs font-mono font-medium">{value}</span>
        <span className={cn('text-[11px] font-mono flex items-center gap-0.5', change >= 0 ? 'text-success' : 'text-danger')}>
          {change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
          {change >= 0 ? '+' : ''}{change}%
        </span>
      </div>
    </div>
  );
}
