import { create } from 'zustand';
import type { Bot } from '@/domains/bot/types';
import type { CycleMessage, AlertMessage, TradeMessage } from '@/domains/system/types';

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

  selectedSymbol: null,
  setSelectedSymbol: (selectedSymbol) => set({ selectedSymbol }),

  livePrices: {},
}));
