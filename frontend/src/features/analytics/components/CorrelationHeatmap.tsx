import React from 'react';
import { cn } from '@/core/utils';

interface CorrelationHeatmapProps {
  data: {
    symbols: string[];
    matrix: number[][];
    window?: number;
    timeframe?: string;
  };
  compact?: boolean;
  loading?: boolean;
}

function cellClass(value: number): string {
  // Strong Positive Correlation
  if (value >= 0.8) return 'bg-success text-success-foreground';
  if (value >= 0.6) return 'bg-success/60 text-success-foreground';
  
  // Moderate Positive Correlation
  if (value >= 0.4) return 'bg-success/30 text-success';
  if (value >= 0.2) return 'bg-success/15 text-success';
  
  // Near Neutral Correlation
  if (value > -0.2 && value < 0.2) return 'bg-secondary/40 text-muted-foreground';
  
  // Moderate Negative Correlation
  if (value <= -0.8) return 'bg-danger text-danger-foreground';
  if (value <= -0.6) return 'bg-danger/60 text-danger-foreground';
  
  // Moderate Negative Correlation
  if (value <= -0.4) return 'bg-danger/30 text-danger';
  if (value <= -0.2) return 'bg-danger/15 text-danger';
  
  return 'bg-secondary/40 text-muted-foreground';
}

function compactSymbol(symbol: string): string {
  const base = symbol.split('/')[0] || symbol;
  return base.replace(':USDT', '').trim();
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({ data, compact = false, loading = false }) => {
  if (loading) {
    return <div className="h-48 flex items-center justify-center animate-pulse bg-secondary/10 rounded-lg">Loading correlation matrix...</div>;
  }

  if (!data.symbols || !data.symbols.length || !data.matrix || !data.matrix.length) {
    return (
      <div className="h-48 flex items-center justify-center border border-dashed border-border rounded-lg text-muted-foreground text-sm">
        No correlation data available.
      </div>
    );
  }

  const labels = data.symbols.map(compactSymbol);
  const cellPadding = compact ? 'px-2 py-1.5' : 'px-2.5 py-2';

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="px-2 py-1.5 text-left text-muted-foreground font-medium bg-secondary/5 rounded-tl-lg">Asset</th>
              {labels.map((label) => (
                <th key={label} className="px-2 py-1.5 text-center text-muted-foreground font-medium min-w-[64px] bg-secondary/5">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {labels.map((rowLabel, rowIdx) => (
              <tr key={rowLabel}>
                <td className="px-2 py-1.5 font-medium text-foreground bg-secondary/5">{rowLabel}</td>
                {data.matrix[rowIdx].map((value, colIdx) => {
                  const display = typeof value === 'number' && isFinite(value) ? value.toFixed(2) : '--';
                  const diagonal = rowIdx === colIdx;
                  return (
                    <td key={`${rowLabel}-${labels[colIdx]}`} className={cellPadding}>
                      <div
                        className={cn(
                          'rounded-md text-center py-1 font-mono transition-all hover:scale-105',
                          cellClass(value),
                          diagonal && 'ring-1 ring-accent/40 opacity-50'
                        )}
                      >
                        {display}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-[10px] text-muted-foreground px-1">
        <span>Analysis Window: {data.window || 100} cycles</span>
        <div className="flex gap-3">
          <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-success" /> High Correlation</span>
          <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-danger" /> Negative Correlation</span>
        </div>
      </div>
    </div>
  );
};
