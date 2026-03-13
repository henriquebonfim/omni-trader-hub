import type { Bot } from '@/domains/bot/types';
import type { AlertMessage, AppConfig, CycleMessage, TradeMessage } from '@/domains/system/types';
import { create } from 'zustand';

const defaultConfig: AppConfig = {
  mode: 'paper',
  default_timeframe: '15m',
  default_leverage: 1,
  default_position_size_pct: 1,
  auto_strategy_mode: true,
  regime_sensitivity: 0,
  max_daily_loss_pct: 5,
  max_weekly_loss_pct: 10,
  consecutive_loss_limit: 3,
  stop_loss_mode: 'fixed',
  stop_loss_value: 0,
  take_profit_mode: 'fixed',
  take_profit_value: 0,
  trailing_stop_activation_pct: 0,
  trailing_stop_callback_pct: 0,
  black_swan_threshold: 10,
  auto_deleverage_drawdown_pct: 15,
  discord_webhook_url: '',
  notify_trades: true,
  notify_circuit_breakers: true,
  notify_daily_summary: true,
  notify_errors: true,
  notify_strategy_rotations: true,
  notification_cooldown_secs: 60,
  exchange_adapter: 'binance',
};

interface AppState {
  // WS
  wsStatus: 'connected' | 'disconnected' | 'connecting';
  setWsStatus: (s: AppState['wsStatus']) => void;

  // Bots
  bots: Bot[];
  setBots: (bots: Bot[]) => void;
  updateBotFromCycle: (msg: CycleMessage) => void;

  // Alerts
  alerts: AlertMessage[];
  addAlert: (a: AlertMessage) => void;
  clearAlerts: () => void;
  unreadAlerts: number;
  markAlertsRead: () => void;

  // Trade events (live)
  tradeEvents: TradeMessage[];
  addTradeEvent: (t: TradeMessage) => void;

  // Config
  config: AppConfig;
  updateConfig: (config: AppConfig) => void;

  // Selected asset
  selectedSymbol: string | null;
  setSelectedSymbol: (s: string | null) => void;

  // Prices from WS
  livePrices: Record<string, number>;
}

export const useAppStore = create<AppState>((set) => ({
  wsStatus: 'disconnected',
  setWsStatus: (wsStatus) => set({ wsStatus }),

  bots: [],
  setBots: (bots) => set({ bots }),
  updateBotFromCycle: (msg) =>
    set((state) => {
      const prices = { ...state.livePrices, [msg.symbol]: msg.price };
      const bots = state.bots.map((b) =>
        b.id === msg.bot_id
          ? {
              ...b,
              active_strategy: msg.active_strategy,
              regime: msg.regime,
              daily_pnl: msg.daily_pnl,
              daily_pnl_pct: msg.daily_pnl_pct,
              balance_allocated: msg.balance,
              position: msg.position
                ? { ...b.position!, side: msg.position, unrealized_pnl: 0 } as Bot['position']
                : null,
            }
          : b
      );
      return { bots, livePrices: prices };
    }),

  alerts: [],
  addAlert: (a) =>
    set((state) => ({
      alerts: [a, ...state.alerts].slice(0, 100),
      unreadAlerts: state.unreadAlerts + 1,
    })),
  clearAlerts: () => set({ alerts: [] }),
  unreadAlerts: 0,
  markAlertsRead: () => set({ unreadAlerts: 0 }),

  tradeEvents: [],
  addTradeEvent: (t) =>
    set((state) => ({
      tradeEvents: [t, ...state.tradeEvents].slice(0, 50),
    })),

  config: defaultConfig,
  updateConfig: (config) => set({ config }),

  selectedSymbol: null,
  setSelectedSymbol: (selectedSymbol) => set({ selectedSymbol }),

  livePrices: {},
}));
