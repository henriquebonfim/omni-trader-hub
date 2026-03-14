import { describe, it, expect, vi, beforeEach } from 'vitest';
import { updateEnvVars } from '@/domains/system/api';
import type { EnvVariable } from '@/domains/system/types';

// Mock the core API request module
vi.mock('@/core/api', () => ({
  request: vi.fn(),
}));

import { request } from '@/core/api';

describe('updateEnvVars', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('sends correct envelope shape with updates object', async () => {
    const mockVars: EnvVariable[] = [
      { key: 'BINANCE_API_KEY', value: 'new_key', category: 'exchange', masked: false, description: '', requires_restart: true },
      { key: 'MEMGRAPH_HOST', value: 'localhost', category: 'database', masked: false, description: '', requires_restart: true },
    ];

    const mockResponse = { requires_restart: true };
    vi.mocked(request).mockResolvedValueOnce(mockResponse);

    const result = await updateEnvVars(mockVars);

    expect(request).toHaveBeenCalledTimes(1);
    expect(request).toHaveBeenCalledWith('/api/env', {
      method: 'PUT',
      body: JSON.stringify({
        updates: {
          BINANCE_API_KEY: 'new_key',
          MEMGRAPH_HOST: 'localhost',
        },
      }),
    });
    expect(result).toEqual(mockResponse);
  });
});
