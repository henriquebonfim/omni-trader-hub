"""
Tests for the WebSocket feed (WsFeed).

All ccxt.pro network calls are mocked — no broker or live exchange required.
"""

import asyncio
from collections import deque
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from src.ws_feed import WsFeed, _MAX_OHLCV_ROWS, _raw_to_df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_df(
    n: int, start_ts: int = 1_700_000_000_000, freq_ms: int = 60_000
) -> pd.DataFrame:
    """Create a minimal OHLCV DataFrame with *n* rows."""
    timestamps = pd.date_range(
        pd.to_datetime(start_ts, unit="ms"),
        periods=n,
        freq=pd.Timedelta(milliseconds=freq_ms),
    )
    df = pd.DataFrame(
        {
            "open": 50_000.0,
            "high": 50_100.0,
            "low": 49_900.0,
            "close": 50_050.0,
            "volume": 100.0,
        },
        index=timestamps,
    )
    df.index.name = "timestamp"
    return df


def _make_raw(n: int, start_ts: int = 1_700_000_000_000, freq_ms: int = 60_000) -> list:
    """Return a CCXT-style list-of-lists OHLCV with *n* rows."""
    return [
        [start_ts + i * freq_ms, 50_000.0, 50_100.0, 49_900.0, 50_050.0, 100.0]
        for i in range(n)
    ]


def _make_feed(**kwargs) -> WsFeed:
    """Build a WsFeed with a mocked ccxt.pro client."""
    with patch("src.ws_feed.ccxtpro") as mock_ccxtpro:
        mock_client = MagicMock()
        mock_ccxtpro.binanceusdm.return_value = mock_client
        feed = WsFeed(
            symbol="BTC/USDT:USDT",
            timeframes=["1m", "5m"],
            paper_mode=kwargs.get("paper_mode", True),
        )
        feed._client = mock_client  # replace with mock
    return feed


# ---------------------------------------------------------------------------
# _raw_to_df helper
# ---------------------------------------------------------------------------


def test_raw_to_df_shape():
    raw = _make_raw(5)
    df = _raw_to_df(raw)
    assert df.shape == (5, 5)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]


def test_raw_to_df_datetime_index():
    raw = _make_raw(3)
    df = _raw_to_df(raw)
    assert pd.api.types.is_datetime64_any_dtype(df.index)


# ---------------------------------------------------------------------------
# WsFeed initialisation
# ---------------------------------------------------------------------------


def test_ws_feed_init_state():
    feed = _make_feed()
    assert feed._ticker is None
    assert feed._ohlcv == {}
    assert isinstance(feed._fills, deque)
    assert feed._tasks == []
    assert not feed._stopped


def test_ws_feed_timeframes_stored():
    feed = _make_feed()
    assert "1m" in feed._timeframes
    assert "5m" in feed._timeframes


# ---------------------------------------------------------------------------
# seed_ohlcv
# ---------------------------------------------------------------------------


def test_seed_ohlcv_populates_cache():
    feed = _make_feed()
    df = _make_df(50)
    feed.seed_ohlcv("1m", df)
    cached = feed.latest_ohlcv("1m")
    assert cached is not None
    assert len(cached) == 50


def test_seed_ohlcv_empty_df_noop():
    feed = _make_feed()
    feed.seed_ohlcv("1m", pd.DataFrame())
    assert feed.latest_ohlcv("1m") is None


def test_seed_ohlcv_trims_to_max():
    feed = _make_feed()
    df = _make_df(_MAX_OHLCV_ROWS + 100)
    feed.seed_ohlcv("1m", df)
    assert len(feed.latest_ohlcv("1m")) == _MAX_OHLCV_ROWS


def test_seed_ohlcv_overwrites_existing():
    feed = _make_feed()
    feed.seed_ohlcv("1m", _make_df(10))
    feed.seed_ohlcv("1m", _make_df(20))
    assert len(feed.latest_ohlcv("1m")) == 20


# ---------------------------------------------------------------------------
# _merge_ohlcv
# ---------------------------------------------------------------------------


def test_merge_ohlcv_empty_cache_sets_data():
    feed = _make_feed()
    new = _make_df(5)
    feed._merge_ohlcv("1m", new)
    assert len(feed.latest_ohlcv("1m")) == 5


def test_merge_ohlcv_appends_new_row():
    feed = _make_feed()
    base = _make_df(5)
    feed.seed_ohlcv("1m", base)

    # One new row one minute after the last
    last_ts = base.index[-1]
    next_ts = last_ts + pd.Timedelta(minutes=1)
    new_row = pd.DataFrame(
        {
            "open": 51_000.0,
            "high": 51_100.0,
            "low": 50_900.0,
            "close": 51_050.0,
            "volume": 200.0,
        },
        index=pd.DatetimeIndex([next_ts], name="timestamp"),
    )
    feed._merge_ohlcv("1m", new_row)
    assert len(feed.latest_ohlcv("1m")) == 6
    assert float(feed.latest_ohlcv("1m")["close"].iloc[-1]) == 51_050.0


def test_merge_ohlcv_updates_existing_row():
    """Updating the forming candle (same timestamp) should overwrite it."""
    feed = _make_feed()
    base = _make_df(5)
    feed.seed_ohlcv("1m", base)

    # Same timestamp as last row but different close
    last_ts = base.index[-1]
    updated = pd.DataFrame(
        {
            "open": 50_000.0,
            "high": 50_200.0,
            "low": 49_800.0,
            "close": 99_999.0,
            "volume": 300.0,
        },
        index=pd.DatetimeIndex([last_ts], name="timestamp"),
    )
    feed._merge_ohlcv("1m", updated)
    # Still 5 rows (duplicate timestamp replaced)
    assert len(feed.latest_ohlcv("1m")) == 5
    assert float(feed.latest_ohlcv("1m")["close"].iloc[-1]) == 99_999.0


def test_merge_ohlcv_trims_to_max():
    feed = _make_feed()
    feed.seed_ohlcv("1m", _make_df(_MAX_OHLCV_ROWS))
    # Append one more distinct row
    base = feed.latest_ohlcv("1m")
    next_ts = base.index[-1] + pd.Timedelta(minutes=1)
    new_row = pd.DataFrame(
        {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
        index=pd.DatetimeIndex([next_ts], name="timestamp"),
    )
    feed._merge_ohlcv("1m", new_row)
    assert len(feed.latest_ohlcv("1m")) == _MAX_OHLCV_ROWS


# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------


def test_latest_ticker_none_initially():
    feed = _make_feed()
    assert feed.latest_ticker() is None


def test_latest_ticker_returns_stored_value():
    feed = _make_feed()
    feed._ticker = {"last": 42_000.0, "symbol": "BTC/USDT:USDT"}
    assert feed.latest_ticker()["last"] == 42_000.0


def test_latest_ohlcv_none_for_unknown_tf():
    feed = _make_feed()
    assert feed.latest_ohlcv("99m") is None


def test_recent_fills_empty_initially():
    feed = _make_feed()
    assert feed.recent_fills() == []


def test_recent_fills_returns_snapshot():
    feed = _make_feed()
    fill = {"id": "abc", "status": "closed", "filled": 0.1, "average": 50_000.0}
    feed._fills.append(fill)
    snapshot = feed.recent_fills()
    assert len(snapshot) == 1
    assert snapshot[0]["id"] == "abc"


def test_recent_fills_max_50():
    feed = _make_feed()
    for i in range(60):
        feed._fills.append({"id": str(i)})
    assert len(feed.recent_fills()) == 50


# ---------------------------------------------------------------------------
# start / stop lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_start_creates_tasks_paper_mode():
    feed = _make_feed(paper_mode=True)

    async def _hang():
        await asyncio.sleep(9999)

    feed._client.watch_ticker = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.watch_ohlcv = AsyncMock(side_effect=asyncio.CancelledError)

    await feed.start()
    # paper_mode=True → ticker task + 2 ohlcv tasks, NO orders task
    assert len(feed._tasks) == 3  # ticker + 1m + 5m
    await feed.stop()


@pytest.mark.asyncio
async def test_start_includes_orders_task_in_live_mode():
    feed = _make_feed(paper_mode=False)

    feed._client.watch_ticker = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.watch_ohlcv = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.watch_orders = AsyncMock(side_effect=asyncio.CancelledError)

    await feed.start()
    task_names = [t.get_name() for t in feed._tasks]
    assert "ws-orders" in task_names
    await feed.stop()


@pytest.mark.asyncio
async def test_stop_cancels_all_tasks():
    feed = _make_feed(paper_mode=True)

    feed._client.watch_ticker = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.watch_ohlcv = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.close = AsyncMock()

    await feed.start()
    await feed.stop()

    assert feed._stopped is True
    assert feed._tasks == []


# ---------------------------------------------------------------------------
# Streaming loop: ticker updates cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_ticker_updates_cache():
    feed = _make_feed(paper_mode=True)
    fake_ticker = {"last": 55_000.0, "symbol": "BTC/USDT:USDT"}

    call_count = 0

    async def _watch_ticker(symbol):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return fake_ticker
        raise asyncio.CancelledError

    feed._client.watch_ticker = _watch_ticker
    feed._client.watch_ohlcv = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.close = AsyncMock()

    await feed.start()
    await asyncio.sleep(0.05)  # let tasks run one iteration
    await feed.stop()

    assert feed._ticker is not None
    assert feed._ticker["last"] == 55_000.0


# ---------------------------------------------------------------------------
# Streaming loop: ohlcv merges into cache
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stream_ohlcv_merges_candle():
    feed = _make_feed(paper_mode=True)
    feed.seed_ohlcv("1m", _make_df(10))
    feed.seed_ohlcv("5m", _make_df(10))

    base = feed.latest_ohlcv("1m")
    next_ts_ms = int(base.index[-1].timestamp() * 1000) + 60_000
    raw_update = [[next_ts_ms, 51_000.0, 51_100.0, 50_900.0, 51_050.0, 200.0]]

    call_count = 0

    async def _watch_ohlcv(symbol, tf):
        nonlocal call_count
        call_count += 1
        if call_count == 1 and tf == "1m":
            return raw_update
        raise asyncio.CancelledError

    feed._client.watch_ticker = AsyncMock(side_effect=asyncio.CancelledError)
    feed._client.watch_ohlcv = _watch_ohlcv
    feed._client.close = AsyncMock()

    await feed.start()
    await asyncio.sleep(0.05)
    await feed.stop()

    updated = feed.latest_ohlcv("1m")
    assert updated is not None
    assert len(updated) == 11
    assert float(updated["close"].iloc[-1]) == 51_050.0
