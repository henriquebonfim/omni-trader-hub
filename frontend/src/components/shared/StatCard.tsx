import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'green' | 'red' | 'accent' | 'yellow' | 'default';
  suffix?: string;
  prefix?: string;
  className?: string;
}

const colorMap = {
  green: 'text-success',
  red: 'text-danger',
  accent: 'text-accent',
  yellow: 'text-warning',
  default: 'text-foreground',
};

export function StatCard({ label, value, trend, color = 'default', suffix, prefix, className }: StatCardProps) {
  return (
    <div className={cn('rounded-lg border border-border bg-card p-4', className)}>
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <div className="flex items-center gap-2">
        <span className={cn('text-xl font-semibold font-mono', colorMap[color])}>
          {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
        </span>
        {trend === 'up' && <TrendingUp className="h-4 w-4 text-success" />}
        {trend === 'down' && <TrendingDown className="h-4 w-4 text-danger" />}
        {trend === 'neutral' && <Minus className="h-4 w-4 text-muted-foreground" />}
      </div>
    </div>
  );
}
