"""
Walk-Forward Analysis Runner.

Fetches historical data and executes backtests over rolling time windows
to assess strategy robustness and parameter stability.
"""

import logging
from typing import Any

import pandas as pd

from src.application.backtest.engine import BacktestEngine
from src.application.backtest.metrics import generate_walk_forward_splits
from src.config import Config
from src.infrastructure.exchanges.base import BaseExchange
from src.domain.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)


class WalkForwardRunner:
    def __init__(
        self,
        config: Config,
        strategy: BaseStrategy,
        exchange: BaseExchange,
        initial_balance: float = 10000.0,
    ):
        self.config = config
        self.strategy = strategy
        self.exchange = exchange
        self.initial_balance = initial_balance
        self.engine = BacktestEngine(
            strategy=self.strategy, config=self.config, initial_balance=self.initial_balance
        )

    async def fetch_data(
        self, symbol: str, timeframe: str, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """Fetch historical OHLCV data."""
        # This is a simplified fetcher; a real implementation would handle pagination
        # and convert start/end dates to milliseconds.
        # For now, we assume exchange's fetch_ohlcv can handle it or we use a large limit.
        logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
        candles = await self.exchange.fetch_candles(
            symbol=symbol, timeframe=timeframe, limit=5000  # Large limit for demo
        )
        return candles

    async def run(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        train_months: int,
        test_months: int,
    ) -> dict[str, Any]:
        """
        Run a full walk-forward analysis.
        """
        candles = await self.fetch_data(symbol, timeframe, start_date, end_date)
        if not candles:
            logger.error("No data fetched, cannot run walk-forward analysis.")
            return {}

        splits = generate_walk_forward_splits(
            candles, train_months=train_months, test_months=test_months
        )

        if not splits:
            logger.warning("Not enough data to generate any walk-forward splits.")
            return {"summary": "Not enough data", "results": []}

        all_results = []
        for i, split in enumerate(splits):
            logger.info(f"Running split {i+1}/{len(splits)}...")

            # In a real scenario, you would re-optimize parameters on the train set.
            # For now, we just run the backtest on the test set.

            test_results = self.engine.run(split["test"])

            split_summary = {
                "split_index": i,
                "train_start": split["train_start"],
                "train_end": split["train_end"],
                "test_start": split["test_start"],
                "test_end": split["test_end"],
                "metrics": test_results["metrics"],
            }
            all_results.append(split_summary)

        # Aggregate results
        summary_metrics = self.summarize_results(all_results)

        return {"summary": summary_metrics, "results": all_results}

    def summarize_results(self, all_results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Aggregate metrics from all walk-forward splits.
        """
        if not all_results:
            return {}

        df = pd.DataFrame([r["metrics"] for r in all_results])

        summary = {
            "num_splits": len(all_results),
            "avg_sharpe": df["sharpe_ratio"].mean(),
            "avg_profit_factor": df["profit_factor"].mean(),
            "avg_win_rate": df["win_rate"].mean(),
            "avg_net_profit": df["net_profit"].mean(),
            "total_net_profit": df["net_profit"].sum(),
            "sharpe_over_time": df["sharpe_ratio"].tolist(),
        }

        return summary
