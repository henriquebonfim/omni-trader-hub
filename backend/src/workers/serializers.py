"""
Serialization helpers for passing Pandas DataFrames through Celery / Redis.

We use the "split" orientation which:
- Is compact
- Preserves column names and index
- Survives JSON round-trips for numeric data

Usage::

    json_str = df_to_json(df)
    df = json_to_df(json_str)
"""

import io
import json

import pandas as pd


def df_to_json(df: pd.DataFrame) -> str:
    """Serialize a DataFrame to a JSON string (split orientation)."""
    return df.to_json(orient="split", date_format="iso")


def json_to_df(json_str: str) -> pd.DataFrame:
    """Deserialize a JSON string (split orientation) back to a DataFrame."""
    df = pd.read_json(io.StringIO(json_str), orient="split")
    # Attempt to restore DatetimeIndex if the index looks like timestamps
    try:
        df.index = pd.to_datetime(df.index)
        df.index.name = "timestamp"
    except Exception:
        pass
    return df


def market_data_to_json(market_data: dict[str, pd.DataFrame]) -> str:
    """
    Serialize a ``{timeframe: DataFrame}`` dict to JSON.

    Returns a JSON object mapping timeframe → split-oriented DataFrame payload.
    """
    return json.dumps({tf: json.loads(df_to_json(df)) for tf, df in market_data.items()})


def json_to_market_data(json_str: str) -> dict[str, pd.DataFrame]:
    """Deserialize a JSON string back to a ``{timeframe: DataFrame}`` dict."""
    raw = json.loads(json_str)
    result: dict[str, pd.DataFrame] = {}
    for tf, payload in raw.items():
        df = pd.DataFrame(
            data=payload["data"],
            columns=payload["columns"],
            index=payload["index"],
        )
        # Attempt to restore DatetimeIndex
        try:
            df.index = pd.to_datetime(df.index)
            df.index.name = "timestamp"
        except Exception:
            pass
        result[tf] = df
    return result
