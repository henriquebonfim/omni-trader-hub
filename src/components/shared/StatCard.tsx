import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  suffix?: string;
  prefix?: string;
  className?: string;
  variant?: 'default' | 'green' | 'red' | 'accent';
}

export function StatCard({ label, value, trend, suffix = '', prefix = '', className, variant = 'default' }: StatCardProps) {
  const valueColorClass = {
    default: 'text-foreground',
    green: 'text-trading-green',
    red: 'text-trading-red',
    accent: 'text-primary',
  }[variant];

  return (
    <div className={cn('rounded-lg bg-card border border-border p-4 space-y-1', className)}>
      <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
      <div className="flex items-center gap-2">
        <span className={cn('text-xl font-bold tabular-nums', valueColorClass)}>
          {prefix}{typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value}{suffix}
        </span>
        {trend === 'up' && <TrendingUp className="h-4 w-4 text-trading-green" />}
        {trend === 'down' && <TrendingDown className="h-4 w-4 text-trading-red" />}
        {trend === 'neutral' && <Minus className="h-4 w-4 text-muted-foreground" />}
      </div>
    </div>
  );
}
