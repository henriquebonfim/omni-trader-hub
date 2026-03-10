"""Test configuration and fixtures."""

import sys
import types

import numpy as np
import pandas as pd


def _install_talib_fallback() -> None:
    """Provide a small TA-Lib-compatible fallback for test environments."""

    talib = types.ModuleType("talib")

    def EMA(values, timeperiod=14):
        series = pd.Series(values, dtype="float64")
        return series.ewm(span=timeperiod, adjust=False).mean().to_numpy()

    def SMA(values, timeperiod=14):
        series = pd.Series(values, dtype="float64")
        return series.rolling(window=timeperiod).mean().to_numpy()

    def ATR(high, low, close, timeperiod=14):
        high_s = pd.Series(high, dtype="float64")
        low_s = pd.Series(low, dtype="float64")
        close_s = pd.Series(close, dtype="float64")
        prev_close = close_s.shift(1)
        tr = pd.concat(
            [(high_s - low_s), (high_s - prev_close).abs(), (low_s - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        return tr.rolling(window=timeperiod).mean().to_numpy()

    def RSI(values, timeperiod=14):
        series = pd.Series(values, dtype="float64")
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(window=timeperiod).mean()
        loss = (-delta.clip(upper=0)).rolling(window=timeperiod).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50).to_numpy()

    def _plus_minus_dm(high_s: pd.Series, low_s: pd.Series):
        up = high_s.diff()
        down = -low_s.diff()
        plus_dm = up.where((up > down) & (up > 0), 0.0)
        minus_dm = down.where((down > up) & (down > 0), 0.0)
        return plus_dm, minus_dm

    def PLUS_DI(high, low, close, timeperiod=14):
        high_s = pd.Series(high, dtype="float64")
        low_s = pd.Series(low, dtype="float64")
        atr = pd.Series(ATR(high, low, close, timeperiod=timeperiod))
        plus_dm, _ = _plus_minus_dm(high_s, low_s)
        plus_di = 100 * (
            plus_dm.rolling(window=timeperiod).mean() / atr.replace(0, np.nan)
        )
        return plus_di.fillna(0).to_numpy()

    def MINUS_DI(high, low, close, timeperiod=14):
        high_s = pd.Series(high, dtype="float64")
        low_s = pd.Series(low, dtype="float64")
        atr = pd.Series(ATR(high, low, close, timeperiod=timeperiod))
        _, minus_dm = _plus_minus_dm(high_s, low_s)
        minus_di = 100 * (
            minus_dm.rolling(window=timeperiod).mean() / atr.replace(0, np.nan)
        )
        return minus_di.fillna(0).to_numpy()

    def ADX(high, low, close, timeperiod=14):
        plus = pd.Series(PLUS_DI(high, low, close, timeperiod=timeperiod))
        minus = pd.Series(MINUS_DI(high, low, close, timeperiod=timeperiod))
        dx = ((plus - minus).abs() / (plus + minus).replace(0, np.nan)) * 100
        return dx.rolling(window=timeperiod).mean().fillna(0).to_numpy()

    def BBANDS(values, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0):
        series = pd.Series(values, dtype="float64")
        mid = series.rolling(window=timeperiod).mean()
        std = series.rolling(window=timeperiod).std(ddof=0)
        upper = mid + (std * nbdevup)
        lower = mid - (std * nbdevdn)
        return upper.to_numpy(), mid.to_numpy(), lower.to_numpy()

    talib.EMA = EMA
    talib.SMA = SMA
    talib.ATR = ATR
    talib.RSI = RSI
    talib.ADX = ADX
    talib.PLUS_DI = PLUS_DI
    talib.MINUS_DI = MINUS_DI
    talib.BBANDS = BBANDS

    sys.modules["talib"] = talib


def _install_celery_fallback() -> None:
    """Provide a minimal Celery-compatible fallback for eager unit tests."""

    celery = types.ModuleType("celery")

    class _Result:
        def __init__(self, value):
            self._value = value

        def get(self, timeout=None):
            return self._value

    class _TaskWrapper:
        def __init__(self, func, bind):
            self._func = func
            self._bind = bind

        def apply(self, args=(), kwargs=None):
            kwargs = kwargs or {}
            if self._bind:
                # Minimal task instance exposing retry used by task code.
                task_self = types.SimpleNamespace(
                    retry=lambda exc=None, countdown=None: (_ for _ in ()).throw(
                        exc or RuntimeError("retry")
                    )
                )
                value = self._func(task_self, *args, **kwargs)
            else:
                value = self._func(*args, **kwargs)
            return _Result(value)

        def __call__(self, *args, **kwargs):
            if self._bind:
                task_self = types.SimpleNamespace(
                    retry=lambda exc=None, countdown=None: (_ for _ in ()).throw(
                        exc or RuntimeError("retry")
                    )
                )
                return self._func(task_self, *args, **kwargs)
            return self._func(*args, **kwargs)

    class Celery:
        def __init__(self, name, broker=None, backend=None, include=None):
            self.conf = types.SimpleNamespace(
                broker_url=broker,
                result_backend=backend,
                update=self._update,
            )

        def _update(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self.conf, k, v)

        def task(self, bind=False, name=None, max_retries=None):
            def decorator(func):
                return _TaskWrapper(func, bind=bind)

            return decorator

    celery.Celery = Celery
    sys.modules["celery"] = celery


def _install_neo4j_fallback() -> None:
    """Provide lightweight neo4j symbols for import-time compatibility in tests."""

    neo4j = types.ModuleType("neo4j")
    neo4j.AsyncDriver = object
    neo4j.AsyncGraphDatabase = object

    exceptions = types.ModuleType("neo4j.exceptions")

    class DriverError(Exception):
        pass

    class Neo4jError(Exception):
        pass

    exceptions.DriverError = DriverError
    exceptions.Neo4jError = Neo4jError

    sys.modules["neo4j"] = neo4j
    sys.modules["neo4j.exceptions"] = exceptions


def _install_feedparser_fallback() -> None:
    feedparser = types.ModuleType("feedparser")
    feedparser.parse = lambda *args, **kwargs: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = feedparser


try:
    import talib  # noqa: F401
except Exception:
    _install_talib_fallback()

try:
    import celery  # noqa: F401
except Exception:
    _install_celery_fallback()

try:
    import neo4j  # noqa: F401
except Exception:
    _install_neo4j_fallback()

try:
    import feedparser  # noqa: F401
except Exception:
    _install_feedparser_fallback()
