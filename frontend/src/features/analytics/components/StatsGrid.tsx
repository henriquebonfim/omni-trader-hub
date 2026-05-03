import React from 'react';
import { TrendingUp, Activity, BarChart3, AlertCircle } from 'lucide-react';
import { StatCard } from '@/shared/ui/molecules/StatCard';

interface StatsGridProps {
  stats: {
    sharpe_ratio: number;
    max_drawdown: number;
    profit_factor: number | string;
    win_rate: number;
    total_trades: number;
  } | null;
  loading?: boolean;
}

export const StatsGrid: React.FC<StatsGridProps> = ({ stats, loading }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Sharpe Ratio"
        value={loading ? '...' : stats?.sharpe_ratio.toString() || '0.00'}
        subtitle="Risk-adjusted return (Annualized)"
        trend={stats && stats.sharpe_ratio > 1 ? 'up' : 'neutral'}
        color={stats && stats.sharpe_ratio > 1 ? 'green' : 'default'}
      />
      <StatCard
        label="Max Drawdown"
        value={loading ? '...' : `${((stats?.max_drawdown || 0) * 100).toFixed(2)}%`}
        subtitle="Largest peak-to-trough decline"
        trend={stats && stats.max_drawdown < -0.15 ? 'down' : 'up'}
        color={stats && stats.max_drawdown < -0.15 ? 'red' : 'green'}
      />
      <StatCard
        label="Profit Factor"
        value={loading ? '...' : stats?.profit_factor.toString() || '0.00'}
        subtitle="Gross Profit / Gross Loss"
        color="accent"
      />
      <StatCard
        label="Win Rate"
        value={loading ? '...' : `${stats?.win_rate || 0}%`}
        subtitle={`Based on ${stats?.total_trades || 0} trades`}
        trend={stats && stats.win_rate > 50 ? 'up' : 'neutral'}
        color={stats && stats.win_rate > 50 ? 'green' : 'default'}
      />
    </div>
  );
};
