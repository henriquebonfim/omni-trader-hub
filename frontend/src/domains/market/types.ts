export interface NewsItem {
  id: string;
  title: string;
  source: string;
  published_at: number;
  sentiment_score: number;
  impact_level: number;
  assets: string[];
  sectors: string[];
}

export interface SentimentData {
  score: number;
  label: string;
  article_count: number;
  max_impact: number;
}

export interface MarketPair {
  symbol: string;
  base: string;
  quote: string;
  volume_24h: number;
  last_price: number;
}
