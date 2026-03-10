import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '@/app/store/app-store';
import type { CycleMessage, AlertMessage, TradeMessage } from '@/domains/system/types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export function useLiveFeed() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>();
  const retryCount = useRef(0);
  const {
    wsStatus, setWsStatus,
    updateBotFromCycle, addAlert, addTradeEvent
  } = useAppStore();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsStatus('connected');
        retryCount.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case 'cycle_update':
              updateBotFromCycle(data as CycleMessage);
              break;
            case 'alert':
              addAlert(data as AlertMessage);
              break;
            case 'trade':
              addTradeEvent(data as TradeMessage);
              break;
          }
        } catch (e) {
          console.error('WS parse error:', e);
        }
      };

      ws.onclose = () => {
        setWsStatus('disconnected');
        const delay = Math.min(1000 * Math.pow(2, retryCount.current), 30000);
        retryCount.current++;
        reconnectTimeout.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      setWsStatus('disconnected');
    }
  }, [setWsStatus, updateBotFromCycle, addAlert, addTradeEvent]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);

  return { status: wsStatus };
}
