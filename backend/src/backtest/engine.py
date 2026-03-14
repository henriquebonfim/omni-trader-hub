import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from src.backtest.metrics import calculate_metrics
from src.config import Config
from src.strategy.base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Event-driven backtesting engine.
    Iterates over historical candles, evaluates strategy signals, simulates execution,
    including bar-level Stop Loss / Take Profit tracking.
    """

    def __init__(
        self, strategy: BaseStrategy, config: Config, initial_balance: float = 10000.0
    ):
        self.strategy = strategy
        self.config = config
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.current_position: Optional[Dict[str, Any]] = None
        self.trades: List[Dict[str, Any]] = []
        self.signals: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.symbol = config.trading.symbol
        self.timeframe = config.trading.timeframe

        # We store history in a dataframe for strategy calculation
        self._history: List[Dict[str, Any]] = []

    def _execute_trade(
        self,
        side: str,
        price: float,
        timestamp: int,
        size: float,
        reason: str,
        pnl: float = 0.0,
        pnl_pct: float = 0.0,
    ):
        trade = {
            "timestamp": timestamp,
            "symbol": self.symbol,
            "side": side,
            "price": price,
            "size": size,
            "reason": reason,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "balance": self.balance,
        }
        self.trades.append(trade)
        return trade

    def _open_position(self, side: str, price: float, timestamp: int, reason: str):
        # Simplistic sizing based on fixed percentage of balance or pure absolute
        # using config default if applicable
        risk_pct = getattr(self.config.risk, "max_position_size_pct", 10.0) / 100.0
        notional = self.balance * risk_pct
        size = notional / price

        sl_pct = getattr(self.config.risk, "stop_loss_pct", 0.0) / 100.0
        tp_pct = getattr(self.config.risk, "take_profit_pct", 0.0) / 100.0

        sl_price = None
        tp_price = None

        if sl_pct > 0:
            sl_price = price * (1 - sl_pct) if side == "long" else price * (1 + sl_pct)
        if tp_pct > 0:
            tp_price = price * (1 + tp_pct) if side == "long" else price * (1 - tp_pct)

        self.current_position = {
            "side": side,
            "entry_price": price,
            "size": size,
            "entry_time": timestamp,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "notional": notional,
        }

        self._execute_trade(side, price, timestamp, size, reason)

    def _close_position(self, price: float, timestamp: int, reason: str):
        if not self.current_position:
            return

        side = self.current_position["side"]
        entry_price = self.current_position["entry_price"]
        size = self.current_position["size"]

        if side == "long":
            pnl = (price - entry_price) * size
            pnl_pct = (price - entry_price) / entry_price
        else:
            pnl = (entry_price - price) * size
            pnl_pct = (entry_price - price) / entry_price

        # Deduct fees
        fee_rate = getattr(self.config.trading, "fee_rate", 0.001)  # 0.1% default
        entry_fee = (entry_price * size) * fee_rate
        exit_fee = (price * size) * fee_rate
        pnl -= entry_fee + exit_fee

        self.balance += pnl

        self._execute_trade(
            side="exit_" + side,
            price=price,
            timestamp=timestamp,
            size=size,
            reason=reason,
            pnl=pnl,
            pnl_pct=pnl_pct,
        )

        self.current_position = None

    def _check_sl_tp(self, candle: Dict[str, Any]) -> bool:
        """
        Check if the current candle triggers SL or TP.
        Returns True if the position was closed.
        """
        if not self.current_position:
            return False

        high = candle["high"]
        low = candle["low"]
        timestamp = candle["timestamp"]
        side = self.current_position["side"]
        sl_price = self.current_position.get("sl_price")
        tp_price = self.current_position.get("tp_price")

        closed = False

        # To avoid ambiguity of what hit first in a bar, we take the worst case if both hit
        # (hitting SL is preferred over TP for conservative backtesting)
        hit_sl = False
        hit_tp = False

        if side == "long":
            if sl_price and low <= sl_price:
                hit_sl = True
            if tp_price and high >= tp_price:
                hit_tp = True
        else:
            if sl_price and high >= sl_price:
                hit_sl = True
            if tp_price and low <= tp_price:
                hit_tp = True

        if hit_sl and hit_tp:
            # Conservative assumption: SL hit first
            self._close_position(sl_price, timestamp, "stop_loss")
            closed = True
        elif hit_sl:
            self._close_position(sl_price, timestamp, "stop_loss")
            closed = True
        elif hit_tp:
            self._close_position(tp_price, timestamp, "take_profit")
            closed = True

        return closed

    def run(self, candles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute the backtest over the provided historical candles.
        Returns a summary dictionary of metrics and the trade log.
        """
        self.balance = self.initial_balance
        self.trades = []
        self.signals = []
        self.equity_curve = []
        self.current_position = None
        self._history = []

        # Convert to list to be safe, sort by timestamp
        sorted_candles = sorted(candles, key=lambda x: x["timestamp"])

        # Buffer to keep only required candles for strategy calculation (to save memory/time)
        max_buffer_size = max(1000, self.strategy.required_candles + 100)

        for _i, candle in enumerate(sorted_candles):
            # 1. Update history
            self._history.append(candle)
            if len(self._history) > max_buffer_size:
                self._history.pop(0)

            # Snapshot equity
            current_equity = self.balance
            if self.current_position:
                # Unrealized PnL based on close price
                close_price = candle["close"]
                entry_price = self.current_position["entry_price"]
                size = self.current_position["size"]
                if self.current_position["side"] == "long":
                    unrealized = (close_price - entry_price) * size
                else:
                    unrealized = (entry_price - close_price) * size
                current_equity += unrealized

            self.equity_curve.append(
                {"timestamp": candle["timestamp"], "equity": current_equity}
            )

            # 2. Check SL/TP on the CURRENT bar
            if self._check_sl_tp(candle):
                continue

            # 3. Strategy evaluation
            # Wait until we have enough candles
            if len(self._history) < self.strategy.required_candles:
                continue

            # Create DataFrame for the strategy
            # To avoid same-bar bias, normally strategy analyzes data UP TO the current bar's close.
            # In live trading, this is equivalent to the close of the last finalized bar.
            df = pd.DataFrame(self._history)

            # Since backtest evaluates on candle close, the 'current' candle is fully formed.
            # Strategy base expects timestamp index (or default int index)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)

            market_data = {self.timeframe: df}

            # Analyze
            current_pos_str = (
                self.current_position["side"] if self.current_position else None
            )
            result = self.strategy.analyze(
                market_data=market_data, ohlcv=df, current_position=current_pos_str
            )

            # Log signal
            if result.signal != Signal.HOLD:
                self.signals.append(
                    {
                        "timestamp": candle["timestamp"],
                        "signal": result.signal.value,
                        "reason": result.reason,
                        "price": candle["close"],
                    }
                )

            # 4. Execute signals at the close price
            if result.signal == Signal.LONG and not self.current_position:
                self._open_position(
                    "long", candle["close"], candle["timestamp"], result.reason
                )
            elif result.signal == Signal.SHORT and not self.current_position:
                self._open_position(
                    "short", candle["close"], candle["timestamp"], result.reason
                )
            elif (
                result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT)
                and self.current_position
            ):
                self._close_position(
                    candle["close"], candle["timestamp"], result.reason
                )

        # Close any open position at the end of the backtest
        if self.current_position and sorted_candles:
            self._close_position(
                sorted_candles[-1]["close"],
                sorted_candles[-1]["timestamp"],
                "end_of_backtest",
            )

        metrics = calculate_metrics(self.trades, self.initial_balance)

        return {
            "metrics": metrics,
            "trades": self.trades,
            "signals": self.signals,
            "equity_curve": self.equity_curve,
        }

    def export_summary(self, result: Dict[str, Any], filepath: str) -> None:
        """
        Export a JSON summary of the backtest results.
        """
        summary = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "initial_balance": self.initial_balance,
            "metrics": result.get("metrics", {}),
        }
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=4)

    def export_trades_csv(self, result: Dict[str, Any], filepath: str) -> None:
        """
        Export the trade log to a CSV file.
        """
        trades = result.get("trades", [])
        if not trades:
            logger.warning("No trades to export to CSV.")
            return

        df = pd.DataFrame(trades)
        if "timestamp" in df.columns:
            # Convert timestamp to human readable format for CSV
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.to_csv(filepath, index=False)
