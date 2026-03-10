import { cn } from '@/core/utils';

interface StatusBadgeProps {
  children: React.ReactNode;
  variant: 'success' | 'danger' | 'warning' | 'info' | 'neutral';
  pulse?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

const variantStyles = {
  success: 'bg-success/15 text-success border-success/30',
  danger: 'bg-danger/15 text-danger border-danger/30',
  warning: 'bg-warning/15 text-warning border-warning/30',
  info: 'bg-accent/15 text-accent border-accent/30',
  neutral: 'bg-muted text-muted-foreground border-border',
};

export function StatusBadge({ children, variant, pulse, size = 'sm', className }: StatusBadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 rounded border font-medium',
      size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs',
      variantStyles[variant],
      className,
    )}>
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', {
            'bg-success': variant === 'success',
            'bg-danger': variant === 'danger',
            'bg-warning': variant === 'warning',
            'bg-accent': variant === 'info',
          })} />
          <span className={cn('relative inline-flex rounded-full h-1.5 w-1.5', {
            'bg-success': variant === 'success',
            'bg-danger': variant === 'danger',
            'bg-warning': variant === 'warning',
            'bg-accent': variant === 'info',
            'bg-muted-foreground': variant === 'neutral',
          })} />
        </span>
      )}
      {children}
    </span>
  );
}
