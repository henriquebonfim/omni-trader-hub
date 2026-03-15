import pytest
from src.backtest.engine import BacktestEngine
from src.strategy.base import BaseStrategy
from src.config import Config
from unittest.mock import MagicMock

class MockStrategy(BaseStrategy):
    required_candles = 1
    def analyze(self, **kwargs):
        pass
    @property
    def metadata(self): return {}
    def should_long(self): return False
    def should_short(self): return False
    def should_exit(self): return False
    @property
    def valid_regimes(self): return []
    def update(self, config): pass

def test_slippage_and_spread_model():
    mock_config_data = {
        "trading": {"symbol": "BTC/USDT", "timeframe": "1h", "fee_rate": 0.0},
        "backtest": {"slippage_bps": 2.0, "spread_bps": 1.0},
        "risk": {},
    }
    config = Config(mock_config_data)
    strategy = MockStrategy(config)
    engine = BacktestEngine(strategy=strategy, config=config)

    # Test Long Position Open
    initial_price = 10000.0
    engine._open_position("long", initial_price, 0, "test")

    spread_adj = initial_price * (1 + 0.0001 / 2)  # spread_bps / 10000
    expected_fill_price_long = spread_adj * (1 + 0.0002)  # slippage_bps / 10000

    assert engine.current_position["entry_price"] == pytest.approx(
        expected_fill_price_long
    )

    # Test Long Position Close
    close_price = 10100.0
    engine._close_position(close_price, 1, "test")

    # Sell lower on close
    spread_adj_close = close_price * (1 - 0.0001 / 2)
    expected_fill_price_long_close = spread_adj_close * (1 - 0.0002)

    final_pnl_long = (
        expected_fill_price_long_close - expected_fill_price_long
    ) * engine.trades[-1]["size"]
    # We ignore fees for this isolated test
    assert engine.trades[-1]["pnl"] == pytest.approx(final_pnl_long)

    # Reset for short test
    engine.current_position = None
    engine.balance = 10000.0

    # Test Short Position Open
    engine._open_position("short", initial_price, 2, "test")

    # Sell lower on open
    spread_adj_short = initial_price * (1 - 0.0001 / 2)
    expected_fill_price_short = spread_adj_short * (1 - 0.0002)

    assert engine.current_position["entry_price"] == pytest.approx(
        expected_fill_price_short
    )

    # Test Short Position Close
    engine._close_position(close_price, 3, "test")

    # Buy higher on close
    spread_adj_short_close = close_price * (1 + 0.0001 / 2)
    expected_fill_price_short_close = spread_adj_short_close * (1 + 0.0002)

    final_pnl_short = (
        expected_fill_price_short - expected_fill_price_short_close
    ) * engine.trades[-1]["size"]
    assert engine.trades[-1]["pnl"] == pytest.approx(final_pnl_short)
