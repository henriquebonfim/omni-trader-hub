from typing import Any, Dict, List

import numpy as np


def calculate_metrics(
    trades: List[Dict[str, Any]], initial_balance: float
) -> Dict[str, Any]:
    """
    Calculate performance metrics from a list of trades.

    trades: List of dicts, each containing:
        - "pnl": float (Absolute PnL of the trade)
        - "pnl_pct": float (Percentage PnL of the trade)
    """
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "max_win_streak": 0,
            "max_loss_streak": 0,
            "net_profit": 0.0,
            "final_balance": initial_balance,
        }

    pnls = [t.get("pnl", 0.0) for t in trades]
    pnl_pcts = [t.get("pnl_pct", 0.0) for t in trades]

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
    cumulative_profit = np.cumsum(pnls)
    equity_curve = initial_balance + cumulative_profit
    peak = np.maximum.accumulate(equity_curve)
    drawdowns = (peak - equity_curve) / peak
    max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0

    # Ratios
    # Assuming risk free rate is 0
    mean_return = np.mean(pnl_pcts)
    std_return = np.std(pnl_pcts)

    # annualized factor (assuming trades are somewhat distributed, but let's just use raw per trade for now or typical 252 factor if daily)
    # Since we don't have time strictly tied here, we'll calculate per-trade Sharpe
    sharpe_ratio = (mean_return / std_return) if std_return > 0 else 0.0

    downside_returns = [r for r in pnl_pcts if r < 0]
    downside_std = np.std(downside_returns) if downside_returns else 0.0
    sortino_ratio = (mean_return / downside_std) if downside_std > 0 else 0.0

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
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "net_profit": float(net_profit),
        "final_balance": float(final_balance),
    }


def bootstrap_confidence_intervals(
    trades: List[Dict[str, Any]], iterations: int = 1000, confidence_level: float = 0.95
) -> Dict[str, Any]:
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
    candles: List[Dict[str, Any]], train_months: int = 6, test_months: int = 1
) -> List[Dict[str, Any]]:
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
