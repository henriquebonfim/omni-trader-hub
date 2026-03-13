const BASE = import.meta.env.VITE_API_URL || '';
let API_KEY = import.meta.env.VITE_API_KEY || '';
let keyPromise: Promise<string> | null = null;

async function getApiKey(): Promise<string> {
  if (API_KEY) return API_KEY;
  if (keyPromise) return keyPromise;
  keyPromise = fetch(`${BASE}/api/auth/key`)
    .then(res => res.json())
    .then(data => {
      if (data.api_key) {
        API_KEY = data.api_key;
        return API_KEY;
      }
      throw new Error('No API key available');
    });
  return keyPromise;
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const key = await getApiKey();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (key) {
    headers['Authorization'] = `Bearer ${key}`;
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
