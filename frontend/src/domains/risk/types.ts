export interface CircuitBreaker {
  name: string;
  limit: string;
  current: string;
  current_pct: number;
  status: 'ok' | 'warning' | 'triggered';
}
