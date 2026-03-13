const BASE = import.meta.env.VITE_API_URL || '';

function getApiKey(): string {
  // Try localStorage first (user-provided at login)
  const storedKey = localStorage.getItem('omnitrader_api_key');
  if (storedKey) return storedKey;
  
  // Fallback to build-time env var
  return import.meta.env.VITE_API_KEY || '';
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const apiKey = getApiKey();
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
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

export function setApiKey(key: string): void {
  localStorage.setItem('omnitrader_api_key', key);
}

export function getStoredApiKey(): string | null {
  return localStorage.getItem('omnitrader_api_key');
}

export function clearApiKey(): void {
  localStorage.removeItem('omnitrader_api_key');
}
