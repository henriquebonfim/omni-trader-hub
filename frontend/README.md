# OmniTrader Frontend

Real-time trading dashboard for the OmniTrader system.

## Features

- **Live Market Monitoring**: Real-time price charts and order books.
- **Bot Management**: Create, start, stop, and monitor multiple trading bot instances.
- **Risk Monitor**: Visual circuit breaker status and daily/weekly PnL tracking.
- **Strategy Lab**: Backtesting interface and parameter optimization (Work in Progress).
- **Intelligence Dashboard**: News feed and sentiment analysis visualization.

## Tech Stack

- **React + Vite**: Fast development and optimized build.
- **TypeScript**: Type safety across the dashboard.
- **Tailwind CSS + shadcn/ui**: Modern, responsive UI components.
- **TanStack Query**: Efficient data fetching and caching.
- **Lucide React**: Clean and consistent iconography.
- **TradingView Lightweight Charts**: High-performance financial charting.

## Getting Started

### Prerequisites

- Node.js 20+
- Bun (recommended) or npm/yarn.

### Setup

```bash
# Install dependencies
bun install

# Configure environment
cp .env.example .env.local
```

### Development

```bash
# Start development server
bun dev
```

### Build

```bash
# Create production build
bun run build
```

## Project Structure

- `src/app/`: Layout and global state.
- `src/core/`: API client and WebSocket management.
- `src/domains/`: Domain-specific logic, components, and types (Bot, Market, Risk, etc.).
- `src/pages/`: Top-level page components.
- `src/shared/`: Reusable UI components and hooks.
- `src/tests/`: Unit, integration, and E2E tests.
