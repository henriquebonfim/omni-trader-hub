import { Panel } from '@/core/shared/Panel';
import { StatCard } from '@/core/shared/StatCard';
import { StatusBadge } from '@/core/shared/StatusBadge';
import { SentimentEmoji, getSentimentLabel } from '@/core/shared/SentimentEmoji';
import { ProgressBar } from '@/core/shared/ProgressBar';
import { CycleMessage } from '@/core/api/ws';
import { mockNewsItems } from '@/core/api/mock-data';
import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { Button } from '@/core/ui/button';

interface IntelligenceProps {
  data: CycleMessage;
}

function timeAgo(ts: number) {
  const diff = (Date.now() - ts) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function impactBadge(level: number) {
  if (level >= 0.7) return <StatusBadge variant="danger">🔴 HIGH</StatusBadge>;
  if (level >= 0.4) return <StatusBadge variant="warning">🟡 MED</StatusBadge>;
  return <StatusBadge variant="info">🟢 LOW</StatusBadge>;
}

export default function Intelligence({ data }: IntelligenceProps) {
  const [newsFilter, setNewsFilter] = useState<'all' | 'high' | 'BTC' | 'ETH'>('all');
  const [alertDismissed, setAlertDismissed] = useState(false);
  const [crisisMode, setCrisisMode] = useState(data.crisis_mode ?? false);
  const sentiment = data.sentiment ?? 0.65;
  const macro = data.macro_indicators ?? { fear_greed: 72, dxy: 104.2, oil: 78.5, btc_dominance: 56.3 };

  const filteredNews = mockNewsItems.filter((n) => {
    if (newsFilter === 'high') return n.impact_level >= 0.7;
    if (newsFilter === 'BTC') return n.assets.includes('BTC');
    if (newsFilter === 'ETH') return n.assets.includes('ETH');
    return true;
  });

  return (
    <div className="space-y-4 animate-slide-in">
      <h1 className="text-lg font-bold text-foreground">🧠 Intelligence</h1>

      {/* Divergence Alert */}
      {data.divergence_flag && !alertDismissed && (
        <div className="flex items-start gap-3 p-3 rounded-lg bg-trading-yellow/10 border border-trading-yellow/30 text-sm">
          <AlertTriangle className="h-5 w-5 text-trading-yellow shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium text-trading-yellow">⚠️ Sentiment-Reality Divergence</p>
            <p className="text-muted-foreground mt-0.5">
              Fear/Greed at {macro.fear_greed.toFixed(0)} (Greed) but news sentiment {sentiment > 0 ? '+' : ''}{sentiment.toFixed(1)} ({getSentimentLabel(sentiment)}). Reducing LONG signal confidence.
            </p>
          </div>
          <button onClick={() => setAlertDismissed(true)} className="text-muted-foreground hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Sentiment Overview */}
        <Panel title="Sentiment Overview">
          <div className="flex items-center gap-6">
            <SentimentEmoji score={sentiment} size="lg" />
            <div className="space-y-1">
              <div className="text-2xl font-bold text-foreground">
                {sentiment > 0 ? '+' : ''}{sentiment.toFixed(2)}
              </div>
              <div className={`text-sm font-medium ${sentiment >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                {getSentimentLabel(sentiment)}
              </div>
              <div className="flex items-center gap-3 mt-2">
                <StatusBadge variant="info">📰 {mockNewsItems.length} articles</StatusBadge>
                {impactBadge(0.8)}
              </div>
            </div>
          </div>
        </Panel>

        {/* Crisis Mode */}
        <Panel title="Crisis Mode Control">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className={`h-4 w-4 rounded-full ${crisisMode ? 'bg-trading-red animate-pulse-slow' : 'bg-trading-green'}`} />
              <span className={`text-lg font-bold ${crisisMode ? 'text-trading-red' : 'text-trading-green'}`}>
                {crisisMode ? 'CRISIS MODE ACTIVE' : 'NORMAL TRADING'}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-muted rounded p-2">
                <div className="text-muted-foreground">Leverage</div>
                <div className="font-bold text-foreground">{crisisMode ? '1.0×' : '3.0×'}</div>
              </div>
              <div className="bg-muted rounded p-2">
                <div className="text-muted-foreground">Position</div>
                <div className="font-bold text-foreground">{crisisMode ? '0.5%' : '2.0%'}</div>
              </div>
              <div className="bg-muted rounded p-2">
                <div className="text-muted-foreground">Strategies</div>
                <div className="font-bold text-foreground">{crisisMode ? 'ADX Only' : 'All Active'}</div>
              </div>
            </div>
            <Button
              onClick={() => setCrisisMode(!crisisMode)}
              variant="outline"
              className={crisisMode ? 'border-trading-green/30 text-trading-green hover:bg-trading-green/10' : 'border-trading-red/30 text-trading-red hover:bg-trading-red/10'}
            >
              {crisisMode ? 'Disable Crisis Mode' : 'Activate Crisis Mode'}
            </Button>
          </div>
        </Panel>
      </div>

      {/* Macro Indicators */}
      <Panel title="Macro Indicators">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-muted rounded-lg p-4 space-y-2">
            <p className="text-xs text-muted-foreground">Fear & Greed</p>
            <p className="text-2xl font-bold text-foreground">{macro.fear_greed.toFixed(0)}</p>
            <ProgressBar value={macro.fear_greed} max={100} variant="auto" />
            <p className="text-xs text-muted-foreground">{macro.fear_greed > 75 ? 'Extreme Greed' : macro.fear_greed > 55 ? 'Greed' : macro.fear_greed > 45 ? 'Neutral' : 'Fear'}</p>
          </div>
          <div className="bg-muted rounded-lg p-4 space-y-2">
            <p className="text-xs text-muted-foreground">DXY Index</p>
            <p className="text-2xl font-bold text-foreground">{macro.dxy.toFixed(1)}</p>
            <ProgressBar value={macro.dxy} max={120} variant="blue" />
          </div>
          <div className="bg-muted rounded-lg p-4 space-y-2">
            <p className="text-xs text-muted-foreground">Oil WTI</p>
            <p className="text-2xl font-bold text-foreground">${macro.oil.toFixed(1)}</p>
            <ProgressBar value={macro.oil} max={120} variant="yellow" />
          </div>
          <div className="bg-muted rounded-lg p-4 space-y-2">
            <p className="text-xs text-muted-foreground">BTC Dominance</p>
            <p className="text-2xl font-bold text-foreground">{macro.btc_dominance.toFixed(1)}%</p>
            <ProgressBar value={macro.btc_dominance} max={100} variant="blue" />
          </div>
        </div>
      </Panel>

      {/* News Feed */}
      <Panel
        title="News Feed"
        actions={
          <div className="flex gap-1">
            {(['all', 'high', 'BTC', 'ETH'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setNewsFilter(f)}
                className={`px-2 py-1 text-xs rounded capitalize ${newsFilter === f ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
              >
                {f === 'high' ? 'High Impact' : f === 'all' ? 'All' : f}
              </button>
            ))}
          </div>
        }
      >
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredNews.map((item) => (
            <div key={item.id} className="flex items-start gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors">
              <div className="shrink-0 mt-0.5">{impactBadge(item.impact_level)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground leading-snug">{item.title}</p>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  <span className="text-xs text-muted-foreground">{item.source}</span>
                  <span className="text-xs text-muted-foreground">·</span>
                  <span className="text-xs text-muted-foreground">{timeAgo(item.published_at)}</span>
                  <span className="text-xs text-muted-foreground">·</span>
                  <span className="text-xs">
                    <SentimentEmoji score={item.sentiment_score} size="sm" />
                    <span className={`ml-1 ${item.sentiment_score >= 0 ? 'text-trading-green' : 'text-trading-red'}`}>
                      {item.sentiment_score > 0 ? '+' : ''}{item.sentiment_score.toFixed(1)}
                    </span>
                  </span>
                </div>
                <div className="flex gap-1 mt-1.5 flex-wrap">
                  {item.assets.map((a) => (
                    <span key={a} className="px-1.5 py-0.5 text-xs rounded bg-primary/10 text-primary">{a}</span>
                  ))}
                  {item.sectors.map((s) => (
                    <span key={s} className="px-1.5 py-0.5 text-xs rounded bg-trading-purple/10 text-trading-purple">{s}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
