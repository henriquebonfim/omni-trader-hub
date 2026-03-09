import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max: number;
  variant?: 'green' | 'red' | 'yellow' | 'blue' | 'auto';
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ value, max, variant = 'auto', showLabel, className }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (Math.abs(value) / Math.abs(max)) * 100));

  const barColor = variant === 'auto'
    ? pct < 50 ? 'bg-trading-green' : pct < 80 ? 'bg-trading-yellow' : 'bg-trading-red'
    : {
        green: 'bg-trading-green',
        red: 'bg-trading-red',
        yellow: 'bg-trading-yellow',
        blue: 'bg-primary',
      }[variant];

  return (
    <div className={cn('space-y-1', className)}>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className={cn('h-full rounded-full transition-all duration-500', barColor)} style={{ width: `${pct}%` }} />
      </div>
      {showLabel && (
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{value.toFixed(1)}</span>
          <span>{max}</span>
        </div>
      )}
    </div>
  );
}
