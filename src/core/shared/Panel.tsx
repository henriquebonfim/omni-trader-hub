import { cn } from '@/core/utils';

interface PanelProps {
  title?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export function Panel({ title, children, actions, className }: PanelProps) {
  return (
    <div className={cn('rounded-lg bg-card border border-border', className)}>
      {(title || actions) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          {title && <h3 className="text-sm font-semibold text-foreground">{title}</h3>}
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
