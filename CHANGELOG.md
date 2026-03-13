# Changelog

All notable changes to OmniTrader will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed 401 Unauthorized errors in frontend by adding /api/auth/key endpoint for dev mode API key retrieval

## [1.0.0] - 2026-03-05

### 🎉 Initial Release - Institutional Audit Complete

This is the first stable release of OmniTrader following a comprehensive institutional-grade security and correctness audit. All critical, high-priority, and medium-priority findings have been resolved.

### 🔴 Critical Fixes (Capital-at-Risk Bugs - T6-T12)

- **T6**: Fixed SL/TP placement failure - now retries 3× or flattens position immediately ([#56](https://github.com/henriquebonfim/omnitrader/pull/56))
- **T7**: Fixed paper mode PnL calculation formula (contract-based, not percentage-based)
- **T8**: Added paper mode SL/TP simulation engine
- **T9**: Wired ATR stops to exchange orders (dynamic volatility-based stops)
- **T10**: Fixed current_positions hardcoded to 0 - now queries actual position count
- **T11**: Added authentication to all API mutation endpoints ([verify_api_key](https://github.com/henriquebonfim/omnitrader/commit/2eb8213))
- **T12**: Hardened Redis risk-state persistence - fail fast on critical errors ([#58](https://github.com/henriquebonfim/omnitrader/pull/58))

### 🟠 High Priority Fixes (Correctness & Reliability - T13-T21)

- **T13**: Added Schmitt-trigger hysteresis to regime detection ([#56](https://github.com/henriquebonfim/omnitrader/pull/56))
- **T14**: Fixed Breakout strategy Donchian bug - now uses prior-bar channel ([#59](https://github.com/henriquebonfim/omnitrader/pull/59))
- **T15**: Added entry cooldown for level-based strategies ([#57](https://github.com/henriquebonfim/omnitrader/pull/57))
- **T16**: Implemented peak-equity high-water mark for drawdown tracking ([#60](https://github.com/henriquebonfim/omnitrader/pull/60))
- **T17**: Fixed consecutive loss streak to persist across day boundaries ([#61](https://github.com/henriquebonfim/omnitrader/pull/61))
- **T18**: Added market order amount validation at exchange boundary ([#62](https://github.com/henriquebonfim/omnitrader/pull/62))
- **T19**: Added WebSocket staleness detection with REST fallback ([#63](https://github.com/henriquebonfim/omnitrader/pull/63))
- **T20**: Added comprehensive Postgres integration tests ([#64](https://github.com/henriquebonfim/omnitrader/pull/64))
- **T21**: Implemented Alembic database migration framework ([#65](https://github.com/henriquebonfim/omnitrader/pull/65))

### 🟡 Medium Priority Fixes (Hardening & Hygiene - T22-T28)

- **T22**: Fixed auth fail-open - now requires API key even in development ([#64](https://github.com/henriquebonfim/omnitrader/pull/64))
- **T23**: Removed hardcoded Postgres password - now requires POSTGRES_PASSWORD env var ([#64](https://github.com/henriquebonfim/omnitrader/pull/64))
- **T24**: Separated dev/prod dependencies (requirements.txt / requirements-dev.txt)
- **T25**: Added dependency lockfile for reproducible builds
- **T26**: Added circuit breaker to Celery dispatcher for worker health
- **T27**: Fetch minimum order size dynamically from exchange (multi-asset support)
- **T28**: Implemented HTTP session pooling and rate limiting for Discord notifier

### ✅ Foundation (T1-T5)

- **T1**: PostgreSQL database support with connection pooling
- **T2**: Redis-based state persistence layer (anti-amnesia)
- **T3**: Leaky-bucket rate limiter (2000 capacity, 40 units/s refill)
- **T4**: Celery + Redis worker architecture for async task processing
- **T5**: WebSocket integration for real-time ticker, OHLCV, and order streaming

### 📋 Known Limitations

- **DO NOT USE WITH LIVE CAPITAL**: While all audit findings have been addressed, the system has not been tested in production with real capital.
- **Geopolitical Risk**: No mechanism to detect or respond to extreme macro events (e.g., Strait of Hormuz closure, oil spikes)
- **Single-Asset**: Currently optimized for BTC/USDT futures only
- **No Multi-Strategy Portfolio**: Strategies run independently, no portfolio-level risk management

### 🔧 Technical Stack

- Python 3.13 + asyncio
- FastAPI (API)
- Celery (async workers)
- Redis (state persistence)
- PostgreSQL (trade database)
- CCXT Pro (exchange integration)
- React + Vite (dashboard)
- Docker Compose (orchestration)

### 📦 Installation

```bash
# Clone repository
git clone https://github.com/henriquebonfim/omnitrader.git
cd omnitrader

# Configure environment
cp .env.example .env
# Edit .env: Set POSTGRES_PASSWORD (required), API keys, Discord webhook

# Start full stack
docker compose up -d --build

# Access dashboard: http://localhost:3000
# Access API: http://localhost:8000/docs
```

### 🧪 Testing

All critical components have been tested:
- 137 passing pytest tests
- Integration tests for PostgreSQL, Redis, WebSocket, Celery
- Paper trading simulation validated

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards-compatible manner
- **PATCH** version for backwards-compatible bug fixes
