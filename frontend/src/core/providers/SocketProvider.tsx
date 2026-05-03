import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

interface SocketContextType {
  lastMessage: any | null;
  isConnected: boolean;
}

const SocketContext = createContext<SocketContextType>({
  lastMessage: null,
  isConnected: false,
});

export const useSocket = () => useContext(SocketContext);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lastMessage, setLastMessage] = useState<any | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = () => {
    const apiURL = import.meta.env.VITE_API_URL || window.location.origin;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsURL = apiURL.replace(/^http/, wsProtocol) + '/ws/live';

    console.log(`Connecting to WebSocket: ${wsURL}`);
    const ws = new WebSocket(wsURL);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = window.setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error', err);
      ws.close();
    };
  };

  useEffect(() => {
    connect();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return (
    <SocketContext.Provider value={{ lastMessage, isConnected }}>
      {children}
    </SocketContext.Provider>
  );
};
