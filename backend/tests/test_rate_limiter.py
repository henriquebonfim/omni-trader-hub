"""
Tests for LeakyBucketRateLimiter.

Covers:
- Token acquisition / consumption
- Throttling when bucket is empty (sleep + refill)
- Context-manager interface
- Concurrent-safe behaviour (multiple coroutines)
- status() / tokens_available snapshot
- Integration: Exchange._rate_limiter is wired up
"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from src.rate_limiter import (
    DEFAULT_WEIGHT,
    ENDPOINT_WEIGHTS,
    LeakyBucketRateLimiter,
)

# ---------------------------------------------------------------------------
# Basic token consumption
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_acquire_consumes_tokens():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=10.0)
    initial = limiter.tokens_available
    await limiter.acquire("fetch_ohlcv")  # weight = 5
    # tokens_available is approximate; just ensure it decreased
    assert limiter.tokens_available < initial


@pytest.mark.asyncio
async def test_acquire_uses_endpoint_weight_table():
    """acquire() should look up the correct weight from ENDPOINT_WEIGHTS."""
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=100.0)
    start_tokens = limiter._tokens  # full bucket

    weight = ENDPOINT_WEIGHTS["fetch_ohlcv"]  # 5
    await limiter.acquire("fetch_ohlcv")
    assert abs(limiter._tokens - (start_tokens - weight)) < 0.1


@pytest.mark.asyncio
async def test_acquire_uses_explicit_weight_over_table():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=100.0)
    await limiter.acquire("fetch_ohlcv", weight=20)
    assert abs(limiter._tokens - 80.0) < 0.1


@pytest.mark.asyncio
async def test_acquire_unknown_endpoint_uses_default_weight():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=100.0)
    await limiter.acquire("unknown_ccxt_method")
    assert abs(limiter._tokens - (100.0 - DEFAULT_WEIGHT)) < 0.1


# ---------------------------------------------------------------------------
# Throttling (bucket nearly empty)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_acquire_throttles_when_bucket_empty():
    """When the bucket is empty, acquire() should wait for a refill."""
    limiter = LeakyBucketRateLimiter(capacity=10.0, refill_rate=100.0)
    limiter._tokens = 0.0  # drain bucket manually

    t0 = time.monotonic()
    await limiter.acquire(weight=5)  # needs 5 tokens; at 100/s → wait ≥ 0.05 s
    elapsed = time.monotonic() - t0

    assert elapsed >= 0.04, f"Expected throttle wait, got {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_acquire_does_not_throttle_when_sufficient_tokens():
    """With a full bucket, acquire() should return immediately."""
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=10.0)

    t0 = time.monotonic()
    await limiter.acquire("fetch_ticker")  # weight = 1
    elapsed = time.monotonic() - t0

    assert elapsed < 0.05, f"Unexpected throttle delay: {elapsed:.3f}s"


# ---------------------------------------------------------------------------
# Context manager interface
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_throttle_context_manager_acquires_tokens():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=100.0)
    before = limiter._tokens

    async with limiter.throttle("create_order"):
        pass  # weight = 1

    assert limiter._tokens < before


@pytest.mark.asyncio
async def test_throttle_context_manager_explicit_weight():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=100.0)

    async with limiter.throttle(weight=10):
        pass

    assert abs(limiter._tokens - 90.0) < 0.1


# ---------------------------------------------------------------------------
# Token refill over time
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refill_over_time():
    """Tokens refill at the configured rate."""
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=200.0)
    limiter._tokens = 0.0
    limiter._last_refill = time.monotonic()

    await asyncio.sleep(0.1)  # 0.1 s × 200/s = 20 tokens

    # Force refill tick by calling _refill inside the lock
    async with limiter._lock:
        limiter._refill()

    assert limiter._tokens >= 15.0, f"Expected ~20 tokens, got {limiter._tokens:.1f}"


@pytest.mark.asyncio
async def test_refill_capped_at_capacity():
    """Tokens should never exceed capacity."""
    limiter = LeakyBucketRateLimiter(capacity=50.0, refill_rate=1000.0)
    limiter._tokens = 45.0
    limiter._last_refill = time.monotonic() - 10.0  # fake 10 s ago

    async with limiter._lock:
        limiter._refill()

    assert limiter._tokens == 50.0


# ---------------------------------------------------------------------------
# Status / snapshot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_status_returns_expected_keys():
    limiter = LeakyBucketRateLimiter(capacity=200.0, refill_rate=40.0)
    s = limiter.status()
    assert "tokens_available" in s
    assert "capacity" in s
    assert "refill_rate_per_sec" in s
    assert "utilization_pct" in s
    assert s["capacity"] == 200.0
    assert s["refill_rate_per_sec"] == 40.0


@pytest.mark.asyncio
async def test_utilization_pct_full_bucket():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=10.0)
    # Full bucket → 0% utilisation
    assert limiter.status()["utilization_pct"] == 0.0


@pytest.mark.asyncio
async def test_utilization_pct_empty_bucket():
    limiter = LeakyBucketRateLimiter(capacity=100.0, refill_rate=10.0)
    limiter._tokens = 0.0
    limiter._last_refill = time.monotonic()  # just refilled so no additional tokens yet
    s = limiter.status()
    assert s["utilization_pct"] >= 90.0  # near 100 %


# ---------------------------------------------------------------------------
# Concurrency safety
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_acquires_do_not_overdraft():
    """Multiple concurrent coroutines should never cause tokens to go negative."""
    limiter = LeakyBucketRateLimiter(capacity=50.0, refill_rate=1000.0)
    limiter._tokens = 30.0  # 30 tokens available

    async def worker():
        await limiter.acquire(weight=5)

    # 6 workers × 5 weight = 30 tokens exactly; the rest must wait + refill
    await asyncio.gather(*[worker() for _ in range(10)])

    assert limiter._tokens >= -0.01, "Tokens must not go below zero"


# ---------------------------------------------------------------------------
# Integration: Exchange uses the rate limiter
# ---------------------------------------------------------------------------


def test_exchange_has_rate_limiter_instance():
    """Exchange.__init__ should set _rate_limiter to a LeakyBucketRateLimiter."""
    with (
        patch("src.exchanges.ccxt_adapter.get_config") as mock_cfg,
        patch("ccxt.async_support.binance"),
    ):
        mock_cfg.return_value = MagicMock(
            exchange=MagicMock(paper_mode=True, leverage=10),
            trading=MagicMock(symbol="BTC/USDT:USDT", timeframe="5m"),
        )
        from src.exchanges import ExchangeFactory

        ex = ExchangeFactory.create_exchange()
        assert isinstance(ex._rate_limiter, LeakyBucketRateLimiter)
