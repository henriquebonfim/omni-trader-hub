import React from 'react';
import { Bot } from '@/domains/bot/types';
import { startBot, stopBot, restartBot, manualOpenTrade, manualCloseTrade } from '@/domains/bot/api';
import { StatusBadge } from '@/shared/ui/molecules/StatusBadge';
import { Pause, Play, Square, Zap, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/core/utils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

interface BotControlCardProps {
  bot: Bot;
  livePrice?: number;
}

const regimeIcons: Record<string, React.ReactNode> = {
  trending: <TrendingUp className="h-3 w-3" />,
  ranging: <ArrowUpDown className="h-3 w-3" />,
  volatile: <Zap className="h-3 w-3" />,
};

import { TrendingUp, ArrowUpDown } from 'lucide-react';

const regimeColors: Record<string, "success" | "danger" | "warning" | "info" | "neutral"> = {
  trending: 'success',
  ranging: 'info',
  volatile: 'warning',
};

export function BotControlCard({ bot, livePrice }: BotControlCardProps) {
  const queryClient = useQueryClient();

  const startMutation = useMutation({
    mutationFn: (id: string) => startBot(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      toast.success(`Bot ${bot.symbol} started`);
    },
  });

  const stopMutation = useMutation({
    mutationFn: (id: string) => stopBot(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bots'] });
      toast.success(`Bot ${bot.symbol} stopped`);
    },
  });

  const isPending = startMutation.isPending || stopMutation.isPending;

  return (
    <div className="rounded-lg bg-white/5 border border-white/10 p-3 hover:bg-white/10 transition-all group backdrop-blur-sm">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm tracking-tight">{bot.symbol}</span>
          <StatusBadge
            variant={bot.status === 'running' ? 'success' : bot.status === 'paused' ? 'warning' : 'danger'}
            pulse={bot.status === 'running'}
            size="sm"
          >
            {isPending ? 'Working...' : bot.status}
          </StatusBadge>
        </div>
        <span className="font-mono text-sm font-medium">
          {livePrice !== undefined ? `$${livePrice.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : '—'}
        </span>
      </div>

      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <StatusBadge variant="info" size="sm">{bot.active_strategy || '—'}</StatusBadge>
        <StatusBadge variant={bot.mode === 'auto' ? 'info' : 'neutral'} size="sm">{bot.mode}</StatusBadge>
        {bot.regime && (
          <StatusBadge variant={regimeColors[bot.regime]} size="sm">
            {regimeIcons[bot.regime]} {bot.regime.toUpperCase()}
          </StatusBadge>
        )}
      </div>

      <div className="flex items-center justify-between text-xs mb-2">
        <div>
          {bot.position ? (
            <StatusBadge variant={bot.position.side === 'long' ? 'success' : 'danger'} size="sm">
              {bot.position.side.toUpperCase()} {(bot.position.unrealized_pnl ?? 0) >= 0 ? '+' : ''}{(bot.position.unrealized_pnl ?? 0).toFixed(2)}
            </StatusBadge>
          ) : (
            <span className="text-muted-foreground/60">FLAT</span>
          )}
        </div>
        <span className={cn('font-mono font-medium', (bot.daily_pnl ?? 0) >= 0 ? 'text-success' : 'text-danger')}>
          {(bot.daily_pnl ?? 0) >= 0 ? '+' : ''}${(bot.daily_pnl ?? 0).toFixed(2)} ({(bot.daily_pnl_pct ?? 0).toFixed(2)}%)
        </span>
      </div>

      <div className="flex items-center gap-1.5 pt-2 border-t border-white/5">
        {bot.status === 'running' ? (
          <button
            onClick={() => stopMutation.mutate(bot.id)}
            disabled={isPending}
            className="px-2 py-1 rounded text-[11px] bg-warning/10 text-warning hover:bg-warning/20 transition-colors disabled:opacity-50"
            title="Stop Bot"
          >
            <Pause className="h-3 w-3" />
          </button>
        ) : (
          <button
            onClick={() => startMutation.mutate(bot.id)}
            disabled={isPending}
            className="px-2 py-1 rounded text-[11px] bg-success/10 text-success hover:bg-success/20 transition-colors disabled:opacity-50"
            title="Start Bot"
          >
            <Play className="h-3 w-3" />
          </button>
        )}
        
        <button
          onClick={() => restartBot(bot.id)}
          className="px-2 py-1 rounded text-[11px] bg-white/5 text-muted-foreground hover:bg-white/10 transition-colors"
          title="Restart"
        >
          <Zap className="h-3 w-3" />
        </button>

        <Link to={`/bots/${bot.id}`} className="ml-auto px-2 py-1 rounded text-[11px] text-primary hover:bg-primary/10 transition-colors flex items-center gap-1">
          Details <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
    </div>
  );
}
