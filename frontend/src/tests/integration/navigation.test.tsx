import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '@/pages/Dashboard';
import BotsAssets from '@/pages/BotsAssets';
import Intelligence from '@/pages/Intelligence';
import Charts from '@/pages/Charts';
import Backtesting from '@/pages/Backtesting';
import RiskMonitor from '@/pages/RiskMonitor';
import TradeHistory from '@/pages/TradeHistory';
import StrategyLab from '@/pages/StrategyLab';
import SettingsPage from '@/pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('navigation integration tests', () => {
  it('renders Dashboard page correctly', async () => {
    renderWithRouter(<Dashboard />);
    expect(await screen.findByText(/Portfolio/i)).toBeInTheDocument();
  });

  it('renders Bots & Assets page correctly', async () => {
    renderWithRouter(<BotsAssets />);
    expect(await screen.findByRole('heading', { name: /Bots & Assets/i })).toBeInTheDocument();
  });

  it('renders Intelligence page correctly', async () => {
    renderWithRouter(<Intelligence />);
    expect(await screen.findByRole('heading', { name: /Intelligence/i })).toBeInTheDocument();
  });

  it('renders Charts page correctly', async () => {
    renderWithRouter(<Charts />);
    expect(await screen.findByRole('heading', { name: /Charts/i })).toBeInTheDocument();
  });

  it('renders Backtesting page correctly', async () => {
    renderWithRouter(<Backtesting />);
    expect(await screen.findByRole('heading', { name: /Backtesting/i })).toBeInTheDocument();
  });

  it('renders Risk Monitor page correctly', async () => {
    renderWithRouter(<RiskMonitor />);
    expect(await screen.findByRole('heading', { name: /Risk Monitor/i })).toBeInTheDocument();
  });

  it('renders Trade History page correctly', async () => {
    renderWithRouter(<TradeHistory />);
    expect(await screen.findByRole('heading', { name: /Trade History/i })).toBeInTheDocument();
  });

  it('renders Strategy Lab page correctly', async () => {
    renderWithRouter(<StrategyLab />);
    expect(await screen.findByRole('heading', { name: /Strategy Lab/i }, { timeout: 10000 })).toBeInTheDocument();
  });

  it('renders Settings page correctly', async () => {
    renderWithRouter(<SettingsPage />);
    expect(await screen.findByRole('heading', { name: /^Settings$/i, level: 1 })).toBeInTheDocument();
  });
});
