export interface Strategy {
  name: string;
  description: string;
  regime_affinity: 'trending' | 'ranging' | 'volatile' | 'all';
  builtin: boolean;
  win_rate?: number;
  sharpe?: number;
  avg_trade?: number;
  active_bots?: number;
  indicators?: IndicatorConfig[];
  entry_long?: IndicatorCondition[];
  entry_short?: IndicatorCondition[];
  exit_long?: IndicatorCondition[];
  exit_short?: IndicatorCondition[];
  stop_loss_atr_mult?: number;
  take_profit_atr_mult?: number;
  min_bars_between_entries?: number;
}

export interface IndicatorCondition {
  indicator: string;
  operator: '>' | '<' | '>=' | '<=' | 'crosses_above' | 'crosses_below';
  value: number | string;
}

export interface IndicatorConfig {
  function: string;
  params: Record<string, number>;
  output_name: string;
}
