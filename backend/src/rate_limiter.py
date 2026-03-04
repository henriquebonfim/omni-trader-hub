"""
Leaky-Bucket Rate Limiter for Binance Futures API.

Proactively throttles outbound CCXT calls *before* transmission to avoid
exceeding Binance's IP weight limits and triggering temporary IP bans.

Binance Futures API limits:
  - 2400 weight units per minute (rolling window)
  - Hard-ban at 2400; soft warning ~2000-2300

Design: Token-bucket (a.k.a. leaky-bucket fill variant).
  - Bucket capacity = CAPACITY weight units.
  - Tokens refill at REFILL_RATE units/second (continuous).
  - Acquiring `weight` tokens blocks until enough tokens are available.
  - Thread-safe via asyncio.Lock; suitable for the single-event-loop design.
"""

import asyncio
import time

import structlog

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Per-endpoint weight table (Binance Futures USD-M, as of 2024)
# https://binance-docs.github.io/apidocs/futures/en/#endpoint-security-type
# ---------------------------------------------------------------------------
ENDPOINT_WEIGHTS: dict[str, int] = {
    # Market data
    "fetch_ohlcv": 5,
    "fetch_ticker": 1,
    "fetch_tickers": 40,
    "fetch_order_book": 10,
    "fetch_trades": 5,
    # Account / position
    "fetch_balance": 5,
    "fetch_positions": 5,
    "fetch_position": 5,
    "fetch_open_orders": 1,
    "fetch_orders": 5,
    "fetch_closed_orders": 5,
    "fetch_my_trades": 5,
    # Order management
    "create_order": 1,
    "cancel_order": 1,
    "cancel_all_orders": 1,
    # Misc
    "load_markets": 10,
    "set_leverage": 1,
    "set_margin_mode": 1,
}

DEFAULT_WEIGHT = 1


class LeakyBucketRateLimiter:
    """
    Async token-bucket rate limiter for Binance Futures API weight limits.

    Usage::

        limiter = LeakyBucketRateLimiter()

        # Before any CCXT call:
        await limiter.acquire("fetch_ohlcv")
        result = await exchange.fetch_ohlcv(...)

        # Or use the context manager:
        async with limiter.throttle("create_order"):
            result = await exchange.create_order(...)

    Parameters
    ----------
    capacity:
        Maximum weight units the bucket can hold.  Binance hard limit is 2400
        per minute; we use a conservative 2000 to provide headroom.
    refill_rate:
        Weight units restored per second.  Binance window is 60 s so full
        refill in 60 s = 2400/60 = 40 units/s.
    """

    def __init__(
        self,
        capacity: float = 2000.0,
        refill_rate: float = 40.0,  # units / second  (2400 / 60)
    ) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate

        # Start with a full bucket so first calls are not artificially delayed.
        self._tokens: float = capacity
        self._last_refill: float = time.monotonic()
        self._lock = asyncio.Lock()

        logger.info(
            "rate_limiter_initialized",
            capacity=capacity,
            refill_rate_per_sec=refill_rate,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time (must hold _lock)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        gained = elapsed * self.refill_rate
        self._tokens = min(self.capacity, self._tokens + gained)
        self._last_refill = now

    def _seconds_until_available(self, weight: int) -> float:
        """How many seconds until `weight` tokens are available (must hold _lock)."""
        if self._tokens >= weight:
            return 0.0
        deficit = weight - self._tokens
        return deficit / self.refill_rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def acquire(self, endpoint: str = "", weight: int | None = None) -> None:
        """
        Block until `weight` tokens are available, then consume them.

        Parameters
        ----------
        endpoint:
            CCXT method name (e.g. ``"fetch_ohlcv"``).  Used for automatic
            weight look-up when *weight* is not provided.
        weight:
            Explicit weight override.  Falls back to :data:`ENDPOINT_WEIGHTS`
            then :data:`DEFAULT_WEIGHT`.
        """
        cost = (
            weight
            if weight is not None
            else ENDPOINT_WEIGHTS.get(endpoint, DEFAULT_WEIGHT)
        )

        async with self._lock:
            while True:
                self._refill()
                wait_secs = self._seconds_until_available(cost)
                if wait_secs <= 0:
                    break
                logger.debug(
                    "rate_limiter_throttle",
                    endpoint=endpoint,
                    weight=cost,
                    wait_secs=round(wait_secs, 3),
                    tokens_available=round(self._tokens, 1),
                )
                # Release lock while sleeping so other tasks can check state
                self._lock.release()
                try:
                    await asyncio.sleep(wait_secs)
                finally:
                    await self._lock.acquire()

            self._tokens -= cost
            logger.debug(
                "rate_limiter_consumed",
                endpoint=endpoint,
                weight=cost,
                tokens_remaining=round(self._tokens, 1),
            )

    def throttle(self, endpoint: str = "", weight: int | None = None):
        """Async context manager wrapper around :meth:`acquire`."""
        return _ThrottleContext(self, endpoint, weight)

    @property
    def tokens_available(self) -> float:
        """Current token level (approximate; not lock-protected)."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        return min(self.capacity, self._tokens + elapsed * self.refill_rate)

    def status(self) -> dict:
        """Return a snapshot of limiter state (for health / metrics endpoints)."""
        return {
            "tokens_available": round(self.tokens_available, 1),
            "capacity": self.capacity,
            "refill_rate_per_sec": self.refill_rate,
            "utilization_pct": round(
                (1.0 - self.tokens_available / self.capacity) * 100, 1
            ),
        }


class _ThrottleContext:
    """Async context manager returned by :meth:`LeakyBucketRateLimiter.throttle`."""

    def __init__(
        self, limiter: LeakyBucketRateLimiter, endpoint: str, weight: int | None
    ):
        self._limiter = limiter
        self._endpoint = endpoint
        self._weight = weight

    async def __aenter__(self):
        await self._limiter.acquire(self._endpoint, self._weight)
        return self

    async def __aexit__(self, *_):
        pass
