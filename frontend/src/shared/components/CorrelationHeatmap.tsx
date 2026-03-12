import { cn } from '@/core/utils';

import type { CorrelationMatrixData } from '@/domains/market/types';

interface CorrelationHeatmapProps {
  data: CorrelationMatrixData;
  compact?: boolean;
}

function cellClass(value: number): string {
  if (value >= 0.7) return 'bg-success/30 text-success';
  if (value >= 0.4) return 'bg-success/15 text-success';
  if (value <= -0.7) return 'bg-danger/35 text-danger';
  if (value <= -0.4) return 'bg-danger/20 text-danger';
  if (value >= 0.15) return 'bg-warning/20 text-warning';
  if (value <= -0.15) return 'bg-warning/15 text-warning';
  return 'bg-secondary/40 text-muted-foreground';
}

function compactSymbol(symbol: string): string {
  const base = symbol.split('/')[0] || symbol;
  return base.replace(':USDT', '').trim();
}

export function CorrelationHeatmap({ data, compact = false }: CorrelationHeatmapProps) {
  if (!data.symbols.length || !data.matrix.length) {
    return <p className="text-xs text-muted-foreground">No matrix data available.</p>;
  }

  const labels = data.symbols.map(compactSymbol);
  const cellPadding = compact ? 'px-2 py-1.5' : 'px-2.5 py-2';

  return (
    <div className="space-y-2">
      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr>
              <th className="px-2 py-1.5 text-left text-muted-foreground font-medium">Asset</th>
              {labels.map((label) => (
                <th key={label} className="px-2 py-1.5 text-center text-muted-foreground font-medium min-w-[52px]">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {labels.map((rowLabel, rowIdx) => (
              <tr key={rowLabel}>
                <td className="px-2 py-1.5 font-medium text-foreground">{rowLabel}</td>
                {data.matrix[rowIdx].map((value, colIdx) => {
                  const display = Number.isFinite(value) ? value.toFixed(2) : '--';
                  const diagonal = rowIdx === colIdx;
                  return (
                    <td key={`${rowLabel}-${labels[colIdx]}`} className={cellPadding}>
                      <div
                        className={cn(
                          'rounded-md text-center font-mono',
                          cellClass(value),
                          diagonal && 'ring-1 ring-accent/40'
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

      <p className="text-[10px] text-muted-foreground">
        Window: {data.window} bars ({data.timeframe})
      </p>
    </div>
  );
}
