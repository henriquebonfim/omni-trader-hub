import { cn } from '@/core/utils';

interface StatusBadgeProps {
  variant: 'success' | 'danger' | 'warning' | 'info' | 'neutral';
  children: React.ReactNode;
  size?: 'sm' | 'md';
  pulse?: boolean;
}

const variantClasses = {
  success: 'bg-trading-green/15 text-trading-green border-trading-green/30',
  danger: 'bg-trading-red/15 text-trading-red border-trading-red/30',
  warning: 'bg-trading-yellow/15 text-trading-yellow border-trading-yellow/30',
  info: 'bg-primary/15 text-primary border-primary/30',
  neutral: 'bg-muted text-muted-foreground border-border',
};

export function StatusBadge({ variant, children, size = 'sm', pulse }: StatusBadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 rounded-full border font-medium',
      variantClasses[variant],
      size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
      pulse && 'animate-pulse-slow',
    )}>
      {children}
    </span>
  );
}
