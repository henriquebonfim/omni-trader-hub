"""
Technical Indicator Adapters

This module provides a unified interface for technical indicators using TA-Lib,
maintaining API compatibility with the previous pandas-ta implementation.

All functions accept pandas Series as input and return pandas Series or DataFrames
with appropriate column names to minimize breaking changes to existing strategies.
"""

import pandas as pd
import talib


def ema(close: pd.Series, length: int = 14) -> pd.Series:
    """
    Exponential Moving Average

    Args:
        close: Price series
        length: Period length

    Returns:
        Series with EMA values, indexed like input
    """
    result = talib.EMA(close.values, timeperiod=length)
    return pd.Series(result, index=close.index, name=f"EMA_{length}")


def sma(close: pd.Series, length: int = 14) -> pd.Series:
    """
    Simple Moving Average

    Args:
        close: Price series
        length: Period length

    Returns:
        Series with SMA values, indexed like input
    """
    result = talib.SMA(close.values, timeperiod=length)
    return pd.Series(result, index=close.index, name=f"SMA_{length}")


def atr(
    high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14
) -> pd.Series:
    """
    Average True Range

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        length: Period length

    Returns:
        Series with ATR values, indexed like close
    """
    result = talib.ATR(high.values, low.values, close.values, timeperiod=length)
    return pd.Series(result, index=close.index, name=f"ATR_{length}")


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """
    Relative Strength Index

    Args:
        close: Price series
        length: Period length

    Returns:
        Series with RSI values (0-100), indexed like input
    """
    result = talib.RSI(close.values, timeperiod=length)
    return pd.Series(result, index=close.index, name=f"RSI_{length}")


def adx(
    high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14
) -> pd.DataFrame:
    """
    Average Directional Index with directional indicators

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        length: Period length

    Returns:
        DataFrame with columns: ADX_{length}, DMP_{length}, DMN_{length}
        Matches pandas-ta column naming convention
    """
    adx_values = talib.ADX(high.values, low.values, close.values, timeperiod=length)
    plus_di = talib.PLUS_DI(high.values, low.values, close.values, timeperiod=length)
    minus_di = talib.MINUS_DI(high.values, low.values, close.values, timeperiod=length)

    return pd.DataFrame(
        {
            f"ADX_{length}": adx_values,
            f"DMP_{length}": plus_di,
            f"DMN_{length}": minus_di,
        },
        index=close.index,
    )


def bbands(close: pd.Series, length: int = 20, std: float = 2.0) -> pd.DataFrame:
    """
    Bollinger Bands

    Args:
        close: Price series
        length: Period length for moving average
        std: Standard deviation multiplier

    Returns:
        DataFrame with columns: BBL_{length}_{std}, BBM_{length}_{std}, BBU_{length}_{std}
        Matches pandas-ta column naming convention with float formatting
    """
    upper, middle, lower = talib.BBANDS(
        close.values,
        timeperiod=length,
        nbdevup=std,
        nbdevdn=std,
        matype=0,  # 0 = SMA (same as pandas-ta default)
    )

    # Format std as pandas-ta does: 2.0 -> "2.0"
    std_str = f"{std:.1f}"

    return pd.DataFrame(
        {
            f"BBL_{length}_{std_str}": lower,
            f"BBM_{length}_{std_str}": middle,
            f"BBU_{length}_{std_str}": upper,
        },
        index=close.index,
    )


def donchian(
    high: pd.Series, low: pd.Series, lower_length: int = 20, upper_length: int = 20
) -> pd.DataFrame:
    """
    Donchian Channels (custom implementation - not in TA-Lib)

    Calculates highest high and lowest low over specified periods.

    Args:
        high: High price series
        low: Low price series
        lower_length: Period for lower channel (lowest low)
        upper_length: Period for upper channel (highest high)

    Returns:
        DataFrame with columns: DCL_{lower}_{upper}, DCM_{lower}_{upper}, DCU_{lower}_{upper}
        - DCU: Upper channel (highest high)
        - DCM: Middle channel (average of upper and lower)
        - DCL: Lower channel (lowest low)
    """
    # Rolling max for upper channel
    upper_channel = high.rolling(window=upper_length).max()

    # Rolling min for lower channel
    lower_channel = low.rolling(window=lower_length).min()

    # Middle channel is average
    middle_channel = (upper_channel + lower_channel) / 2

    return pd.DataFrame(
        {
            f"DCL_{lower_length}_{upper_length}": lower_channel,
            f"DCM_{lower_length}_{upper_length}": middle_channel,
            f"DCU_{lower_length}_{upper_length}": upper_channel,
        },
        index=high.index,
    )


# Convenience exports for backward compatibility
__all__ = [
    "ema",
    "sma",
    "atr",
    "rsi",
    "adx",
    "bbands",
    "donchian",
]
