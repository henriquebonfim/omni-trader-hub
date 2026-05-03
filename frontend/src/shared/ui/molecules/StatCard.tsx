import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';
import { cn } from '@/core/utils';

interface StatCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'green' | 'red' | 'accent' | 'yellow' | 'blue' | 'default';
  suffix?: string;
  prefix?: string;
  tooltip?: string;
  className?: string;
  children?: React.ReactNode;
}

const colorMap = {
  green: 'text-success',
  red: 'text-danger',
  accent: 'text-accent',
  yellow: 'text-warning',
  blue: 'text-info',
  default: 'text-foreground',
};

export function StatCard({ 
  label, 
  value, 
  subtitle, 
  trend, 
  color = 'default', 
  suffix, 
  prefix, 
  tooltip, 
  className, 
  children 
}: StatCardProps) {
  return (
    <div 
      className={cn('rounded-lg bg-glass p-3 relative group', className)}
      title={tooltip}
    >
      <div className="flex items-center justify-between mb-1">
        <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground">{label}</p>
        {tooltip && <Info className="h-2.5 w-2.5 text-muted-foreground/50 opacity-0 group-hover:opacity-100 transition-opacity" />}
      </div>
      
      <div className="flex items-end justify-between gap-1">
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className={cn('text-lg font-bold font-mono leading-none', colorMap[color])}>
              {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
            </span>
            {trend === 'up' && <TrendingUp className="h-3.5 w-3.5 text-success" />}
            {trend === 'down' && <TrendingDown className="h-3.5 w-3.5 text-danger" />}
            {trend === 'neutral' && <Minus className="h-3.5 w-3.5 text-muted-foreground" />}
          </div>
          {subtitle && <p className="text-[10px] text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        
        {children && <div className="flex-1 max-w-[40%] h-8">{children}</div>}
      </div>
    </div>
  );
}
