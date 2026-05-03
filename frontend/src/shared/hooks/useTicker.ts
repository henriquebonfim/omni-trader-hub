import { useState, useEffect } from 'react';
import { useAppStore } from '@/app/store/app-store';

export function useTicker(symbol: string) {
  const livePrices = useAppStore(s => s.livePrices);
  const wsStatus = useAppStore(s => s.wsStatus);
  const [ticker, setTicker] = useState<{
    price: number;
    change24h?: number;
    high?: number;
    low?: number;
  } | null>(null);

  useEffect(() => {
    const price = livePrices[symbol];
    if (price !== undefined) {
      setTicker({
        price,
      });
    }
  }, [livePrices, symbol]);

  return { ticker, isConnected: wsStatus === 'connected' };
}
