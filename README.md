# Omni-Trader Hub 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-B73BFE?logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**Omni-Trader Hub** is a comprehensive, modern dashboard interface designed for quantitative traders and algorithmic trading bot managers. It features dark-mode aesthetics, rich interactive charts, and an array of components optimized for managing trading backtests, strategies, risk monitors, and live market intelligence.

This project was built to showcase a high-performance frontend implementation using **React, Vite, TypeScript, Tailwind CSS**, and **shadcn-ui**.

> **Note**: This is a frontend-only showcase. The data displayed is mocked for demonstration purposes, ensuring no actual financial data, API keys, or live connections are required to run and interact with the application.

## 🌟 Features

- **Advanced Trading Dashboard**: Overview of portfolio performance, recent trades, and open positions.
- **Interactive Chart Analysis**: Deep technical analysis capabilities using `lightweight-charts`.
- **Strategy Backtesting Interface**: UI for configuring parameters, running simulated tests, and displaying walk-forward analysis metrics.
- **Risk Monitor**: Visual circuit breakers, max drawdown limits, and portfolio health indicators.
- **Market Intelligence**: Live sentiment emojis and news stream interfaces.
- **Responsive & Modern UI**: Built with Radix UI primitives and styled via Tailwind CSS for a seamless dark-theme experience.

## 🛠️ Tech Stack

- **Framework**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Components**: [shadcn/ui](https://ui.shadcn.com/)
- **Charts**: [Lightweight Charts](https://tradingview.github.io/lightweight-charts/), [Recharts](https://recharts.org/)
- **Routing**: [React Router DOM](https://reactrouter.com/)

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps:

### Prerequisites

Ensure you have [Node.js](https://nodejs.org/) (v18 or higher recommended) and `npm` installed.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/alpha-trader-hub.git
   cd alpha-trader-hub
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   Navigate to `http://localhost:8080` (or the port specified by Vite in your terminal).

## 🌍 Deployment

This application is optimized for static hosting platforms like **Firebase Hosting**, Vercel, or Netlify.

### Firebase Hosting

1. Install the Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```
2. Login to Firebase:
   ```bash
   firebase login
   ```
3. Initialize the project (already configured via `firebase.json` in this repo, so you just need to link your project):
   ```bash
   firebase use --add
   ```
4. Build the project:
   ```bash
   npm run build
   ```
5. Deploy:
   ```bash
   firebase deploy --only hosting
   ```

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
