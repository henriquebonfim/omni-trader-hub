import { cn } from '@/core/utils';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface PanelProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  collapsible?: boolean;
  defaultOpen?: boolean;
  className?: string;
  noPadding?: boolean;
}

export function Panel({ title, subtitle, children, actions, collapsible, defaultOpen = true, className, noPadding }: PanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={cn('rounded-lg bg-glass overflow-hidden', className)}>
      {(title || actions) && (
        <div
          className={cn(
            'flex items-center justify-between px-4 py-3 border-b border-border',
            collapsible && 'cursor-pointer select-none hover:bg-secondary/50'
          )}
          onClick={collapsible ? () => setOpen(!open) : undefined}
        >
          <div>
            {title && <h3 className="text-sm font-semibold">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            {collapsible && (open ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />)}
          </div>
        </div>
      )}
      {(!collapsible || open) && (
        <div className={cn(!noPadding && 'p-4')}>
          {children}
        </div>
      )}
    </div>
  );
}
