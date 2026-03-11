import { Panel } from '@/shared/components/Panel';
import { StatusBadge } from '@/shared/components/StatusBadge';
import { StatCard } from '@/shared/components/StatCard';
import { mockNews } from '@/domains/market/mocks';
import { mockAlerts } from '@/domains/system/mocks';
import { cn } from '@/core/utils';
import { useState } from 'react';
import { AlertTriangle, Newspaper, Gauge, Globe, TrendingUp, TrendingDown } from 'lucide-react';

import { fetchSentiment, fetchCrisisStatus, fetchNews } from '@/domains/market/api';
import type { NewsItem, SentimentData } from '@/domains/market/types';
import type { CrisisStatus } from '@/domains/system/types';

export default function Intelligence() {
  const [newsFilter, setNewsFilter] = useState<'all' | 'high' | 'asset'>('all');
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [crisisStatus, setCrisisStatus] = useState<CrisisStatus | null>(null);
  const [news, setNews] = useState<NewsItem[]>(mockNews);

  useEffect(() => {
    fetchSentiment('BTC/USDT').then(setSentimentData).catch(console.error);
    fetchCrisisStatus().then(setCrisisStatus).catch(console.error);
    fetchNews().then(res => {
      if (res && res.length > 0) setNews(res);
    }).catch(console.error);
  }, []);

  const sentiment = sentimentData?.score || 0;
  const crisisActive = crisisStatus?.active || false;

  const filteredNews = newsFilter === 'high'
    ? news.filter(n => n.impact_level > 0.7)
    : news;

  const sentimentLabel = sentiment > 0.5 ? 'Bullish' : sentiment > 0.2 ? 'Slightly Bullish' : sentiment > -0.2 ? 'Neutral' : sentiment > -0.5 ? 'Slightly Bearish' : 'Bearish';
  const sentimentEmoji = sentiment > 0.5 ? '😊' : sentiment > 0.2 ? '🙂' : sentiment > -0.2 ? '😐' : sentiment > -0.5 ? '😟' : '😢';

  return (
    <div className="space-y-4 animate-fade-in">
      <h1 className="text-lg font-semibold">Intelligence</h1>

      {/* Top row */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Sentiment */}
        <Panel title="Market Sentiment">
          <div className="flex items-center gap-4">
            <span className="text-4xl">{sentimentEmoji}</span>
            <div>
              <p className="text-lg font-semibold font-mono">{sentiment.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground">{sentimentLabel}</p>
              <p className="text-[11px] text-muted-foreground mt-1">42 articles (24h)</p>
            </div>
          </div>
        </Panel>

        {/* Crisis Mode */}
        <Panel title="Crisis Mode">
          <div className={cn(
            'rounded-md p-3 border',
            crisisActive ? 'border-danger animate-pulse-border bg-danger/5' : 'border-success/30 bg-success/5'
          )}>
            <p className={cn('text-sm font-semibold', crisisActive ? 'text-danger' : 'text-success')}>
              {crisisActive ? '🚨 CRISIS MODE ACTIVE' : '✅ NORMAL TRADING'}
            </p>
            {crisisActive && (
              <p className="text-[11px] text-muted-foreground mt-1">Leverage: 1×, Position: 0.5%, ADX Trend only</p>
            )}
          </div>
          <button className="mt-3 w-full py-2 rounded-md border border-border text-xs font-medium hover:bg-secondary/50 transition-colors">
            {crisisActive ? 'Deactivate Crisis Mode' : 'Activate Crisis Mode'}
          </button>
        </Panel>

        {/* Fear & Greed */}
        <Panel title="Fear & Greed Index">
          <div className="flex items-center gap-3">
            <div className="relative h-16 w-16">
              <svg viewBox="0 0 36 36" className="h-16 w-16 -rotate-90">
                <circle cx="18" cy="18" r="15" fill="none" stroke="hsl(var(--border))" strokeWidth="3" />
                <circle cx="18" cy="18" r="15" fill="none" stroke="hsl(var(--yellow))" strokeWidth="3"
                  strokeDasharray={`${62 * 94.2 / 100} 94.2`} strokeLinecap="round" />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-sm font-bold font-mono">62</span>
            </div>
            <div>
              <p className="text-sm font-semibold text-warning">Greed</p>
              <p className="text-[11px] text-muted-foreground">+3 from yesterday</p>
            </div>
          </div>
        </Panel>

        {/* Macro */}
        <Panel title="Macro Indicators">
          <div className="space-y-2">
            <MacroRow label="DXY" value="104.2" change={-0.3} />
            <MacroRow label="Oil (WTI)" value="$78.4" change={1.2} />
            <MacroRow label="BTC.D" value="54.8%" change={0.5} />
          </div>
        </Panel>
      </div>

      {/* Divergence alert banner */}
      <div className="rounded-md border border-warning/30 bg-warning/5 p-3 flex items-center gap-3">
        <AlertTriangle className="h-4 w-4 text-warning shrink-0" />
        <div>
          <p className="text-xs font-medium text-warning">Divergence Detected</p>
          <p className="text-[11px] text-muted-foreground">Price action diverging from sentiment on BTC/USDT. Monitor closely.</p>
        </div>
      </div>

      {/* News Feed */}
      <Panel
        title="News Feed"
        actions={
          <div className="flex gap-1">
            {(['all', 'high', 'asset'] as const).map(f => (
              <button
                key={f}
                onClick={() => setNewsFilter(f)}
                className={cn(
                  'px-2 py-0.5 rounded text-[11px] transition-colors capitalize',
                  newsFilter === f ? 'bg-accent/15 text-accent' : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {f === 'high' ? 'High Impact' : f === 'asset' ? 'By Asset' : 'All'}
              </button>
            ))}
          </div>
        }
      >
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {filteredNews.map(item => (
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
                  {item.assets.map(a => (
                    <StatusBadge key={a} variant="neutral" size="sm">{a}</StatusBadge>
                  ))}
                  <span className="text-[10px] text-muted-foreground ml-auto">
                    {Math.floor((Date.now() - item.published_at) / 3600000)}h ago
                  </span>
                </div>
              </div>
            </div>
          ))}
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
