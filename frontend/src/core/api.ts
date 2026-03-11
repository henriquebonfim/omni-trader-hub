const BASE = import.meta.env.VITE_API_URL || '';
const API_KEY = import.meta.env.VITE_API_KEY || '';

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (API_KEY) {
    headers['Authorization'] = `Bearer ${API_KEY}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    headers: { ...headers, ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API Error: ${res.status} ${res.statusText}`);
  
  // Return null if empty response (like 204 No Content)
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}
