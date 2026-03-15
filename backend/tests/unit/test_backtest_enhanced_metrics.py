import pytest
import numpy as np
from src.backtest.metrics import (
    calculate_metrics,
    calculate_information_coefficient,
    calculate_factor_attribution
)

def test_enhanced_metrics_basic():
    trades = [
        {"pnl": 100.0, "pnl_pct": 0.01, "size": 1.0, "price": 10000.0},
        {"pnl": -50.0, "pnl_pct": -0.005, "size": 1.0, "price": 10000.0},
        {"pnl": 200.0, "pnl_pct": 0.02, "size": 1.0, "price": 10000.0},
    ]
    initial_balance = 10000.0
    
    metrics = calculate_metrics(trades, initial_balance)
    
    assert metrics["total_trades"] == 3
    assert metrics["win_rate"] == pytest.approx(0.666, 0.01)
    assert metrics["profit_factor"] == 6.0 # (100+200) / 50
    assert metrics["calmar_ratio"] > 0
    assert metrics["portfolio_turnover"] > 0
    assert metrics["t_stat"] != 0

def test_information_coefficient():
    signals = [
        {"timestamp": 1000, "signal": "long"},
        {"timestamp": 2000, "signal": "short"},
    ]
    candles = [
        {"timestamp": 1000, "close": 100.0},
        {"timestamp": 1100, "close": 105.0}, # +5% for long (perfect)
        {"timestamp": 2000, "close": 100.0},
        {"timestamp": 2100, "close": 95.0},  # -5% for short (perfect)
    ]
    # Need more data for spearmanr to not return NaN or error
    signals = signals * 5
    candles = [
        {"timestamp": 1000, "close": 100.0},
        {"timestamp": 1001, "close": 101.0},
        {"timestamp": 2000, "close": 100.0},
        {"timestamp": 2001, "close": 99.0},
        {"timestamp": 3000, "close": 100.0},
        {"timestamp": 3001, "close": 101.0},
        {"timestamp": 4000, "close": 100.0},
        {"timestamp": 4001, "close": 99.0},
        {"timestamp": 5000, "close": 100.0},
        {"timestamp": 5001, "close": 101.0},
        {"timestamp": 6000, "close": 100.0},
        {"timestamp": 6001, "close": 99.0},
    ]
    signals = [
        {"timestamp": 1000, "signal": "long"},
        {"timestamp": 2000, "signal": "short"},
        {"timestamp": 3000, "signal": "long"},
        {"timestamp": 4000, "signal": "short"},
        {"timestamp": 5000, "signal": "long"},
        {"timestamp": 6000, "signal": "short"},
    ]
    
    ic_data = calculate_information_coefficient(signals, candles, horizons=[1])
    assert "ic_1_bar" in ic_data["ic_decay"]
    assert ic_data["ic_decay"]["ic_1_bar"] == pytest.approx(1.0) # Perfect correlation

def test_factor_attribution():
    equity_curve = [
        {"timestamp": 1000, "equity": 10000.0},
        {"timestamp": 2000, "equity": 10100.0},
        {"timestamp": 3000, "equity": 10050.0},
        {"timestamp": 4000, "equity": 10200.0},
        {"timestamp": 5000, "equity": 10300.0},
        {"timestamp": 6000, "equity": 10250.0},
        {"timestamp": 7000, "equity": 10400.0},
        {"timestamp": 8000, "equity": 10500.0},
    ]
    market_candles = [
        {"timestamp": 1000, "close": 50000.0},
        {"timestamp": 2000, "close": 51000.0},
        {"timestamp": 3000, "close": 50500.0},
        {"timestamp": 4000, "close": 52000.0},
        {"timestamp": 5000, "close": 53000.0},
        {"timestamp": 6000, "close": 52500.0},
        {"timestamp": 7000, "close": 54000.0},
        {"timestamp": 8000, "close": 55000.0},
    ]
    
    factor_data = calculate_factor_attribution(equity_curve, market_candles)
    assert "beta" in factor_data
    # print(f"DEBUG: factor_data={factor_data}")
    assert factor_data["beta"] > 0
    assert factor_data["r_squared"] > 0.5
