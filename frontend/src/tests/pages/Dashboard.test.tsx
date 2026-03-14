import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import Dashboard from '@/pages/Dashboard';
import { useAppStore } from '@/app/store/app-store';
import { BrowserRouter } from 'react-router-dom';

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  LineChart: () => <div>LineChart</div>,
  Line: () => <div>Line</div>,
  XAxis: () => <div>XAxis</div>,
  YAxis: () => <div>YAxis</div>,
  CartesianGrid: () => <div>CartesianGrid</div>,
  Tooltip: () => <div>Tooltip</div>,
  AreaChart: () => <div>AreaChart</div>,
  Area: () => <div>Area</div>,
  defs: () => <div>defs</div>,
  linearGradient: () => <div>linearGradient</div>,
  stop: () => <div>stop</div>,
}));

vi.mock('@/core/api', () => ({
  request: vi.fn(),
}));

describe('Dashboard Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAppStore.setState({ bots: [], tradeEvents: [] });
  });

  it('renders Dashboard empty state initially', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    expect(screen.getAllByText('Active Bots')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Equity Curve')[0]).toBeInTheDocument();
  });
});
