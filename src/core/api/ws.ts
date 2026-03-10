import { useState, useEffect, useRef, useCallback } from 'react';

export interface CycleMessage {
  timestamp: number;
  price: number;
  signal: 'LONG' | 'SHORT' | 'HOLD';
  position: 'long' | 'short' | null;
  balance: number;
  daily_pnl: number;
  daily_pnl_pct: number;
  circuit_breaker: boolean;
  reason?: string;
  sentiment?: number;
  crisis_mode?: boolean;
  macro_indicators?: {
    fear_greed: number;
    dxy: number;
    oil: number;
    btc_dominance: number;
  };
  divergence_flag?: boolean;
}

type WsStatus = 'connecting' | 'open' | 'closed';

export function useLiveFeed() {
  const [message, setMessage] = useState<CycleMessage | null>(null);
  const [status, setStatus] = useState<WsStatus>('connecting');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    setStatus('connecting');
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => setStatus('open');
    ws.onclose = () => {
      setStatus('closed');
      reconnectTimer.current = setTimeout(connect, 5000);
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (event) => {
      try {
        setMessage(JSON.parse(event.data));
      } catch {
        // Ignore JSON parse errors for non-JSON messages like pings
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  return { message, status };
}

// Mock data hook for demo purposes (when no WS available)
export function useMockLiveFeed() {
  const [message, setMessage] = useState<CycleMessage>({
    timestamp: Date.now(),
    price: 67432.50,
    signal: 'LONG',
    position: 'long',
    balance: 10847.32,
    daily_pnl: 234.56,
    daily_pnl_pct: 2.21,
    circuit_breaker: false,
    sentiment: 0.65,
    crisis_mode: false,
    macro_indicators: {
      fear_greed: 72,
      dxy: 104.2,
      oil: 78.5,
      btc_dominance: 56.3,
    },
    divergence_flag: false,
  });
  const [status] = useState<WsStatus>('open');

  useEffect(() => {
    const interval = setInterval(() => {
      setMessage((prev) => ({
        ...prev,
        timestamp: Date.now(),
        price: prev.price + (Math.random() - 0.48) * 100,
        daily_pnl: prev.daily_pnl + (Math.random() - 0.45) * 10,
        daily_pnl_pct: prev.daily_pnl_pct + (Math.random() - 0.45) * 0.1,
        balance: prev.balance + (Math.random() - 0.45) * 15,
        sentiment: Math.max(-1, Math.min(1, (prev.sentiment ?? 0) + (Math.random() - 0.5) * 0.05)),
        macro_indicators: {
          fear_greed: Math.max(0, Math.min(100, (prev.macro_indicators?.fear_greed ?? 72) + (Math.random() - 0.5) * 2)),
          dxy: (prev.macro_indicators?.dxy ?? 104.2) + (Math.random() - 0.5) * 0.1,
          oil: (prev.macro_indicators?.oil ?? 78.5) + (Math.random() - 0.5) * 0.3,
          btc_dominance: (prev.macro_indicators?.btc_dominance ?? 56.3) + (Math.random() - 0.5) * 0.05,
        },
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return { message, status };
}
