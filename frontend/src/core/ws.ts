import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '@/app/store/app-store';
import type { AlertMessage, TradeMessage } from '@/domains/system/types';
import { adaptWsMessage } from '@/lib/adapters';

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
      // Connect relative to current host via proxy, or use absolute URL
      const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.host}/ws/live`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsStatus('connected');
        retryCount.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const rawData = JSON.parse(event.data);
          // Backend sends a raw flat cycle JSON currently, we need to adapt it
          // Check if it's already structured or needs adaptation
          let data = rawData;
          
          if (!rawData.type || rawData.type === 'cycle_update') {
             data = adaptWsMessage(rawData);
          }

          switch (data.type) {
            case 'cycle_update':
              updateBotFromCycle(data);
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
