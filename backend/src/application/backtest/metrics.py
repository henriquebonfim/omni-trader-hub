from typing import Any

import numpy as np
import pandas as pd


def calculate_factor_attribution(
    equity_curve: list[dict[str, Any]], market_candles: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Calculate strategy Alpha and Beta relative to the market.
    For crypto, market is usually BTC/USDT.
    """
    if not equity_curve or not market_candles:
        return {"alpha": 0.0, "beta": 0.0, "r_squared": 0.0}

    # Align data
    eq_df = pd.DataFrame(equity_curve).set_index("timestamp")
    mkt_df = pd.DataFrame(market_candles).set_index("timestamp")

    # Resample or reindex to align
    combined = pd.concat([eq_df["equity"], mkt_df["close"]], axis=1).dropna()
    combined.columns = ["equity", "market"]
    # Calculate returns
    combined["strat_ret"] = combined["equity"].pct_change()
    combined["mkt_ret"] = combined["market"].pct_change()
    combined = combined.dropna()

    if len(combined) < 5:
        return {"alpha": 0.0, "beta": 0.0, "r_squared": 0.0}

    # Linear regression: strat_ret = alpha + beta * mkt_ret
    from scipy import stats

    beta, alpha, r_value, p_value, std_err = stats.linregress(
        combined["mkt_ret"], combined["strat_ret"]
    )

    return {
        "alpha": float(alpha),
        "beta": float(beta),
        "r_squared": float(r_value**2),
        "p_value": float(p_value),
    }


def calculate_information_coefficient(
    signals: list[dict[str, Any]],
    candles: list[dict[str, Any]],
    horizons: list[int] | None = None,
) -> dict[str, Any]:
    """
    Calculate Information Coefficient (IC) and its decay over different horizons.
    IC is the correlation between signal strength and subsequent returns.

    signals: List of {"timestamp": int, "signal": str, "price": float}
    candles: List of OHLCV dicts
    horizons: List of number of bars to look ahead
    """
    if horizons is None:
        horizons = [1, 5, 10, 20]

    if not signals or not candles:
        return {"ic_mean": 0.0, "ic_decay": {}}

    # Convert candles to dataframe for easy lookahead returns
    df = pd.DataFrame(candles)
    if "timestamp" not in df.columns:
        return {"ic_mean": 0.0, "ic_decay": {}}

    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)

    ic_results = {}

    # Signal mapping: LONG=1, SHORT=-1, HOLD=0 (usually only non-hold are logged)
    signal_map = {"long": 1.0, "short": -1.0, "hold": 0.0}

    sig_times = [s["timestamp"] for s in signals]
    sig_values = [signal_map.get(s["signal"].lower(), 0.0) for s in signals]

    for h in horizons:
        returns = []
        valid_sigs = []

        for _i, (ts, val) in enumerate(zip(sig_times, sig_values, strict=False)):
            if ts in df.index:
                # Find the index of the current timestamp
                idx = df.index.get_loc(ts)
                if idx + h < len(df):
                    # h-bar forward return
                    future_price = df.iloc[idx + h]["close"]
                    current_price = df.iloc[idx]["close"]
                    fwd_return = (future_price - current_price) / current_price
                    returns.append(fwd_return)
                    valid_sigs.append(val)

        if len(returns) > 5:
            # Spearman rank correlation is more robust for IC
            from scipy.stats import spearmanr

            correlation, _ = spearmanr(valid_sigs, returns)
            ic_results[f"ic_{h}_bar"] = float(correlation)
        else:
            ic_results[f"ic_{h}_bar"] = 0.0

    ic_values = [v for k, v in ic_results.items()]
    return {
        "ic_mean": float(np.mean(ic_values)) if ic_values else 0.0,
        "ic_decay": ic_results,
    }


def calculate_metrics(
    trades: list[dict[str, Any]],
    initial_balance: float,
    equity_curve: list[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Calculate performance metrics from a list of trades and equity curve.

    trades: List of dicts, each containing:
        - "pnl": float (Absolute PnL of the trade)
        - "pnl_pct": float (Percentage PnL of the trade)
        - "size": float (Size of the trade)
        - "price": float (Entry price)
    equity_curve: Optional list of {"timestamp": int, "equity": float}
    """
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "portfolio_turnover": 0.0,
            "t_stat": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "max_win_streak": 0,
            "max_loss_streak": 0,
            "net_profit": 0.0,
            "final_balance": initial_balance,
        }

    pnls = [t.get("pnl", 0.0) for t in trades if "pnl" in t]
    pnl_pcts = [t.get("pnl_pct", 0.0) for t in trades if "pnl_pct" in t]

    total_trades = len(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    win_rate = len(wins) / total_trades if total_trades > 0 else 0.0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    if gross_loss == 0 and gross_profit == 0:
        profit_factor = 0.0

    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0

    net_profit = sum(pnls)
    final_balance = initial_balance + net_profit

    # Drawdown calculation
    max_drawdown = 0.0
    if equity_curve:
        equities = np.array([e["equity"] for e in equity_curve])
        peaks = np.maximum.accumulate(equities)
        drawdowns = (peaks - equities) / peaks
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
    else:
        # Fallback to trade-based drawdown if equity curve not provided
        cumulative_profit = np.cumsum(pnls)
        trade_equities = initial_balance + cumulative_profit
        peaks = np.maximum.accumulate(trade_equities)
        drawdowns = (peaks - trade_equities) / peaks
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0

    # Ratios
    mean_return = np.mean(pnl_pcts) if pnl_pcts else 0.0
    std_return = np.std(pnl_pcts) if pnl_pcts else 0.0

    sharpe_ratio = (mean_return / std_return) if std_return > 0 else 0.0

    downside_returns = [r for r in pnl_pcts if r < 0]
    downside_std = np.std(downside_returns) if downside_returns else 0.0
    sortino_ratio = (mean_return / downside_std) if downside_std > 0 else 0.0

    # Calmar Ratio: Net Profit % / Max Drawdown
    total_return_pct = net_profit / initial_balance
    calmar_ratio = (
        (total_return_pct / max_drawdown)
        if max_drawdown > 0
        else (float("inf") if total_return_pct > 0 else 0.0)
    )

    # Portfolio Turnover (Simplistic: Sum of |size * price| / avg_balance)
    # This represents how much of the portfolio was 'replaced'
    total_volume = sum(abs(t.get("size", 0.0) * t.get("price", 0.0)) for t in trades)
    avg_balance = (initial_balance + final_balance) / 2
    portfolio_turnover = total_volume / avg_balance if avg_balance > 0 else 0.0

    # T-Stat of returns (mean / (std / sqrt(n)))
    t_stat = 0.0
    if std_return > 0 and total_trades > 0:
        t_stat = mean_return / (std_return / np.sqrt(total_trades))

    # Streaks
    max_win_streak = 0
    max_loss_streak = 0
    current_win_streak = 0
    current_loss_streak = 0

    for p in pnls:
        if p > 0:
            current_win_streak += 1
            current_loss_streak = 0
            if current_win_streak > max_win_streak:
                max_win_streak = current_win_streak
        else:
            current_loss_streak += 1
            current_win_streak = 0
            if current_loss_streak > max_loss_streak:
                max_loss_streak = current_loss_streak

    return {
        "total_trades": total_trades,
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "max_drawdown": float(max_drawdown),
        "sharpe_ratio": float(sharpe_ratio),
        "sortino_ratio": float(sortino_ratio),
        "calmar_ratio": float(calmar_ratio),
        "portfolio_turnover": float(portfolio_turnover),
        "t_stat": float(t_stat),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "net_profit": float(net_profit),
        "final_balance": float(final_balance),
    }


def bootstrap_confidence_intervals(
    trades: list[dict[str, Any]], iterations: int = 1000, confidence_level: float = 0.95
) -> dict[str, Any]:
    """
    Calculate bootstrap confidence intervals for key metrics.
    """
    if not trades or len(trades) < 2:
        return {}

    pnls = np.array([t.get("pnl", 0.0) for t in trades])
    n_trades = len(pnls)

    bootstrap_net_profits = []

    for _ in range(iterations):
        sample = np.random.choice(pnls, size=n_trades, replace=True)
        bootstrap_net_profits.append(np.sum(sample))

    lower_percentile = (1.0 - confidence_level) / 2.0 * 100
    upper_percentile = (1.0 + confidence_level) / 2.0 * 100

    return {
        "net_profit_ci_lower": float(
            np.percentile(bootstrap_net_profits, lower_percentile)
        ),
        "net_profit_ci_upper": float(
            np.percentile(bootstrap_net_profits, upper_percentile)
        ),
    }


def generate_walk_forward_splits(
    candles: list[dict[str, Any]], train_months: int = 6, test_months: int = 1
) -> list[dict[str, Any]]:
    """
    Generate walk-forward train/test splits.
    candles must have "timestamp" in milliseconds.
    """
    if not candles:
        return []

    # Sort candles just in case
    candles = sorted(candles, key=lambda c: c["timestamp"])

    start_ts = candles[0]["timestamp"]
    end_ts = candles[-1]["timestamp"]

    # rough ms conversions
    ms_per_month = 30 * 24 * 60 * 60 * 1000
    train_ms = train_months * ms_per_month
    test_ms = test_months * ms_per_month

    splits = []
    current_start = start_ts

    while current_start + train_ms + test_ms <= end_ts:
        train_end = current_start + train_ms
        test_end = train_end + test_ms

        train_data = [c for c in candles if current_start <= c["timestamp"] < train_end]
        test_data = [c for c in candles if train_end <= c["timestamp"] < test_end]

        if train_data and test_data:
            splits.append(
                {
                    "train": train_data,
                    "test": test_data,
                    "train_start": current_start,
                    "train_end": train_end,
                    "test_start": train_end,
                    "test_end": test_end,
                }
            )

        current_start += test_ms  # slide forward by test window

    return splits
