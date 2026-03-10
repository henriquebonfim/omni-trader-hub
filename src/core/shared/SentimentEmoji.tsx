export function SentimentEmoji({ score, size = 'md' }: { score: number; size?: 'sm' | 'md' | 'lg' }) {
  const emoji = score <= -0.6 ? '😢' : score <= -0.2 ? '😟' : score <= 0.2 ? '😐' : score <= 0.6 ? '🙂' : '😊';
  const sizeClass = { sm: 'text-lg', md: 'text-3xl', lg: 'text-5xl' }[size];
  return <span className={sizeClass} role="img" aria-label="sentiment">{emoji}</span>;
}

export function getSentimentLabel(score: number) {
  if (score <= -0.6) return 'Very Bearish';
  if (score <= -0.2) return 'Bearish';
  if (score <= 0.2) return 'Neutral';
  if (score <= 0.6) return 'Bullish';
  return 'Very Bullish';
}
