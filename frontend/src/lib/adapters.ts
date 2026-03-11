import type { Bot, Position } from '@/domains/bot/types';
import type { Strategy } from '@/domains/strategy/types';
import type { AppConfig, CycleMessage } from '@/domains/system/types';
import type { EquitySnapshot, Trade } from '@/domains/trade/types';

type JsonObject = Record<string, unknown>;

export function adaptBotState(backendStatus: JsonObject, backendPosition: JsonObject, backendBalance: JsonObject): Bot {
  let position: Position | null = null;
  if (backendPosition && backendPosition.is_open) {
    const side = String(backendPosition.side ?? 'long').toLowerCase();
    position = {
      side: (side === 'short' ? 'short' : 'long') as 'long' | 'short',
      entry_price: Number(backendPosition.entry_price ?? 0),
      size: Number(backendPosition.size ?? 0),
      unrealized_pnl: Number(backendPosition.unrealized_pnl ?? 0),
      stop_loss: Number(backendPosition.stop_loss ?? 0),
      take_profit: Number(backendPosition.take_profit ?? 0),
      opened_at: backendPosition.opened_at ? new Date(String(backendPosition.opened_at)).getTime() : Date.now(),
    };
  }

  return {
    id: 'default',
    symbol: String(backendStatus.symbol ?? 'BTC/USDT'),
    status: backendStatus.running ? 'running' : 'stopped',
    mode: 'auto', // default to auto as it's not currently tracked in backend status in this way
    active_strategy: String(backendStatus.strategy ?? 'unknown'),
    regime: (backendStatus.market_regime as Bot['regime']) ?? 'trending', // fallback
    position,
    daily_pnl: Number(backendBalance?.daily_pnl ?? 0),
    daily_pnl_pct: Number(backendBalance?.daily_pnl_pct ?? 0),
    balance_allocated: Number(backendBalance?.total ?? 0),
    leverage: Number(backendPosition?.leverage ?? 1),
    created_at: Date.now() - Number(backendStatus.uptime_seconds ?? 0) * 1000,
  };
}

export function adaptTrade(backendTrade: JsonObject): Trade {
  const maybeStringId = backendTrade.id;
  const numericId = typeof maybeStringId === 'string' ? parseInt(maybeStringId, 10) : Number(maybeStringId);
  return {
    id: Number.isFinite(numericId) ? numericId : 0,
    timestamp: typeof backendTrade.timestamp === 'string' ? new Date(backendTrade.timestamp).getTime() : Number(backendTrade.timestamp ?? Date.now()),
    bot_id: String(backendTrade.bot_id ?? 'default'),
    symbol: String(backendTrade.symbol ?? 'UNKNOWN'),
    side: String(backendTrade.side ?? 'long').toLowerCase() === 'short' ? 'short' : 'long',
    action: String(backendTrade.action ?? 'OPEN').toUpperCase() === 'CLOSE' ? 'CLOSE' : 'OPEN',
    strategy: String(backendTrade.strategy ?? 'unknown'),
    price: Number(backendTrade.price ?? backendTrade.execution_price ?? 0),
    expected_price: backendTrade.expected_price as number | undefined,
    slippage: backendTrade.slippage as number | undefined,
    size: Number(backendTrade.size ?? backendTrade.contracts ?? 0),
    notional: Number(backendTrade.notional ?? (Number(backendTrade.price ?? 0) * Number(backendTrade.size ?? 0))),
    fee: Number(backendTrade.fee ?? 0),
    pnl: backendTrade.pnl as number | undefined,
    pnl_pct: backendTrade.pnl_pct as number | undefined,
    reason: String(backendTrade.reason ?? ''),
    stop_loss: backendTrade.stop_loss as number | undefined,
    take_profit: backendTrade.take_profit as number | undefined,
  };
}

export function adaptEquitySnapshot(backendSnapshot: JsonObject): EquitySnapshot {
  return {
    timestamp: typeof backendSnapshot.timestamp === 'string' ? new Date(backendSnapshot.timestamp).getTime() : Number(backendSnapshot.timestamp ?? Date.now()),
    equity: Number(backendSnapshot.balance ?? backendSnapshot.equity ?? 0),
    bot_id: String(backendSnapshot.bot_id ?? 'default'),
    symbol: backendSnapshot.symbol ? String(backendSnapshot.symbol) : undefined,
  };
}

export function adaptStrategy(backendStrategy: JsonObject): Strategy {
  return {
    name: String(backendStrategy.name ?? ''),
    description: String(backendStrategy.description ?? ((backendStrategy.metadata as JsonObject | undefined)?.description ?? '')),
    regime_affinity: (backendStrategy.regime_affinity as Strategy['regime_affinity']) || 'all',
    builtin: backendStrategy.type !== 'custom',
    win_rate: backendStrategy.win_rate as number | undefined,
    sharpe: (backendStrategy.sharpe_ratio as number | undefined) ?? (backendStrategy.sharpe as number | undefined),
    avg_trade: backendStrategy.avg_trade as number | undefined,
    active_bots: Number(backendStrategy.active_bots ?? 0),
    indicators: backendStrategy.indicators as Strategy['indicators'],
    entry_long: backendStrategy.entry_long as Strategy['entry_long'],
    entry_short: backendStrategy.entry_short as Strategy['entry_short'],
    exit_long: backendStrategy.exit_long as Strategy['exit_long'],
    exit_short: backendStrategy.exit_short as Strategy['exit_short'],
    stop_loss_atr_mult: backendStrategy.stop_loss_atr_mult as number | undefined,
    take_profit_atr_mult: backendStrategy.take_profit_atr_mult as number | undefined,
    min_bars_between_entries: backendStrategy.min_bars_between_entries as number | undefined,
  };
}

export function adaptConfig(backendConfig: JsonObject): AppConfig {
  return {
    mode: (backendConfig.exchange as JsonObject | undefined)?.paper_mode ? 'paper' : 'live',
    default_timeframe: String((backendConfig.trading as JsonObject | undefined)?.timeframe ?? '15m'),
    default_leverage: Number((backendConfig.exchange as JsonObject | undefined)?.leverage ?? 1),
    default_position_size_pct: Number((backendConfig.risk as JsonObject | undefined)?.position_size_pct ?? 1.0),
    auto_strategy_mode: true, // fallback
    regime_sensitivity: 0, // fallback
    max_daily_loss_pct: Number((backendConfig.risk as JsonObject | undefined)?.max_daily_loss_pct ?? 5.0),
    max_weekly_loss_pct: Number((backendConfig.risk as JsonObject | undefined)?.max_weekly_loss_pct ?? 10.0),
    consecutive_loss_limit: Number((backendConfig.risk as JsonObject | undefined)?.consecutive_loss_limit ?? 3),
    stop_loss_mode: (backendConfig.risk as JsonObject | undefined)?.use_atr_stops ? 'atr' : 'fixed',
    stop_loss_value: Number((backendConfig.risk as JsonObject | undefined)?.stop_loss_pct ?? 0),
    take_profit_mode: (backendConfig.risk as JsonObject | undefined)?.use_atr_stops ? 'atr' : 'fixed',
    take_profit_value: Number((backendConfig.risk as JsonObject | undefined)?.take_profit_pct ?? 0),
    trailing_stop_activation_pct: Number((backendConfig.risk as JsonObject | undefined)?.trailing_stop_activation_pct ?? 0),
    trailing_stop_callback_pct: Number((backendConfig.risk as JsonObject | undefined)?.trailing_stop_callback_pct ?? 0),
    black_swan_threshold: Number((backendConfig.risk as JsonObject | undefined)?.black_swan_threshold ?? 10.0),
    auto_deleverage_drawdown_pct: Number((backendConfig.risk as JsonObject | undefined)?.auto_deleverage_drawdown_pct ?? 15.0),
    discord_webhook_url: String((backendConfig.notifications as JsonObject | undefined)?.discord_webhook ?? ''),
    notify_trades: Boolean((backendConfig.notifications as JsonObject | undefined)?.notify_trades ?? true),
    notify_circuit_breakers: Boolean((backendConfig.notifications as JsonObject | undefined)?.notify_circuit_breakers ?? true),
    notify_daily_summary: Boolean((backendConfig.notifications as JsonObject | undefined)?.notify_daily_summary ?? true),
    notify_errors: Boolean((backendConfig.notifications as JsonObject | undefined)?.notify_errors ?? true),
    notify_strategy_rotations: Boolean((backendConfig.notifications as JsonObject | undefined)?.notify_strategy_rotations ?? true),
    notification_cooldown_secs: Number((backendConfig.notifications as JsonObject | undefined)?.cooldown_secs ?? 60),
    exchange_adapter: String((backendConfig.exchange as JsonObject | undefined)?.id ?? 'binance') as AppConfig['exchange_adapter'],
  };
}

export function reverseAdaptConfig(appConfig: AppConfig): JsonObject {
  return {
    exchange: {
      paper_mode: appConfig.mode === 'paper',
      leverage: appConfig.default_leverage,
      id: appConfig.exchange_adapter,
    },
    trading: {
      timeframe: appConfig.default_timeframe,
    },
    risk: {
      position_size_pct: appConfig.default_position_size_pct,
      max_daily_loss_pct: appConfig.max_daily_loss_pct,
      max_weekly_loss_pct: appConfig.max_weekly_loss_pct,
      consecutive_loss_limit: appConfig.consecutive_loss_limit,
      use_atr_stops: appConfig.stop_loss_mode === 'atr',
      stop_loss_pct: appConfig.stop_loss_value,
      take_profit_pct: appConfig.take_profit_value,
      trailing_stop_activation_pct: appConfig.trailing_stop_activation_pct,
      trailing_stop_callback_pct: appConfig.trailing_stop_callback_pct,
      black_swan_threshold: appConfig.black_swan_threshold,
      auto_deleverage_drawdown_pct: appConfig.auto_deleverage_drawdown_pct,
    },
    notifications: {
      discord_webhook: appConfig.discord_webhook_url,
      notify_trades: appConfig.notify_trades,
      notify_circuit_breakers: appConfig.notify_circuit_breakers,
      notify_daily_summary: appConfig.notify_daily_summary,
      notify_errors: appConfig.notify_errors,
      notify_strategy_rotations: appConfig.notify_strategy_rotations,
      cooldown_secs: appConfig.notification_cooldown_secs,
    },
  };
}

export function adaptWsMessage(backendMsg: JsonObject): CycleMessage {
  return {
    type: 'cycle_update',
    bot_id: String(backendMsg.bot_id ?? 'default'),
    symbol: String(backendMsg.symbol ?? 'UNKNOWN'),
    timestamp: Number(backendMsg.timestamp ?? Date.now()),
    price: Number(backendMsg.current_price ?? backendMsg.price ?? 0),
    signal: (backendMsg.signal as CycleMessage['signal']) ?? 'HOLD',
    active_strategy: String(backendMsg.active_strategy ?? backendMsg.strategy ?? 'unknown'),
    regime: (backendMsg.market_regime as CycleMessage['regime']) ?? ((backendMsg.regime as CycleMessage['regime']) ?? 'trending'),
    position: (backendMsg.position as CycleMessage['position']) ?? null,
    balance: Number(backendMsg.balance_allocated ?? backendMsg.balance ?? 0),
    daily_pnl: Number(backendMsg.daily_pnl ?? 0),
    daily_pnl_pct: Number(backendMsg.daily_pnl_pct ?? 0),
    circuit_breaker: Boolean(backendMsg.circuit_breaker_active ?? backendMsg.circuit_breaker ?? false),
    reason: backendMsg.reason ? String(backendMsg.reason) : undefined,
    sentiment: backendMsg.sentiment as number | undefined,
    crisis_mode: backendMsg.crisis_mode as boolean | undefined,
    macro_indicators: backendMsg.macro_indicators as CycleMessage['macro_indicators'],
    divergence_flag: backendMsg.divergence_flag as boolean | undefined,
  };
}
