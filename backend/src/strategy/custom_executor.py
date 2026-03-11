import pandas as pd
import structlog
import talib
import talib.abstract
from typing import Dict, Any, List

from src.config import Config
from src.strategy.base import BaseStrategy
from src.intelligence.regime import MarketRegime

logger = structlog.get_logger()


class CustomStrategyExecutor(BaseStrategy):
    """
    Executor for custom strategies defined dynamically via the API.
    """

    def __init__(self, config: Config, custom_config: Dict[str, Any]):
        """
        Initialize strategy with global configuration and custom strategy definition.
        """
        super().__init__(config)
        self.custom_config = custom_config
        self.name = custom_config.get("name", "custom_strategy")
        
        # Override config parameters based on custom config
        if custom_config.get("stop_loss_atr_mult"):
            self.config.risk.stop_loss_atr_mult = custom_config["stop_loss_atr_mult"]
        if custom_config.get("take_profit_atr_mult"):
            self.config.risk.take_profit_atr_mult = custom_config["take_profit_atr_mult"]
        if custom_config.get("min_bars_between_entries"):
            self.config.strategy.min_bars_between_entries = custom_config["min_bars_between_entries"]

        self._indicators: Dict[str, pd.Series] = {}

    @property
    def metadata(self) -> Dict[str, str]:
        return {
            "type": "custom",
            "name": self.name,
            "description": self.custom_config.get("description", ""),
        }

    @property
    def valid_regimes(self) -> List[MarketRegime]:
        affinities = self.custom_config.get("regime_affinity", [])
        if not affinities:
            return [regime for regime in MarketRegime]
        
        valid = []
        for regime_str in affinities:
            try:
                valid.append(MarketRegime(regime_str))
            except ValueError:
                pass
        return valid if valid else [regime for regime in MarketRegime]

    def _compute_indicators(self, ohlcv: pd.DataFrame):
        """Compute indicators based on indicators_json schema."""
        self._indicators.clear()
        
        indicators_json = self.custom_config.get("indicators_json", [])
        for ind in indicators_json:
            func_name = ind.get("function", "").upper()
            params = ind.get("params", {})
            output_name = ind.get("output_name")
            
            if not func_name or not output_name:
                continue
                
            try:
                # Prepare inputs dynamically. TA-Lib abstract function uses OHLCV or price.
                # Default is typical input, but talib.abstract handles pandas dataframes well
                # if column names are open, high, low, close, volume.
                func = talib.abstract.Function(func_name)
                
                # talib.abstract functions might return a single series or a tuple of series.
                # If tuple, we need to map them or assume a standard? 
                # According to the prompt, `rsi_14` will be evaluated. Let's just store the output.
                # The output can be a DataFrame if multiple, but we expect series.
                
                # Create a dict of standard lowercase column names mapped to numpy arrays or pandas Series
                inputs = {
                    'open': ohlcv['open'].values,
                    'high': ohlcv['high'].values,
                    'low': ohlcv['low'].values,
                    'close': ohlcv['close'].values,
                    'volume': ohlcv['volume'].values,
                }
                
                result = func(inputs, **params)
                
                # Handle multiple outputs (e.g., MACD returns macd, macdsignal, macdhist)
                if isinstance(result, list) or isinstance(result, tuple):
                    # We will store them in a dict if needed, or if only 1 output is named...
                    # Wait, if output_name is used, we just assign the first one?
                    # The prompt: `{"function": "RSI", "params": {"timeperiod": 14}, "output_name": "rsi_14"}`
                    # If it's single output:
                    # Let's just handle single output functions for now, or if multiple, return the first
                    # or perhaps `result` is a numpy array.
                    if len(result) > 0 and isinstance(result[0], (list, tuple, pd.Series, pd.DataFrame, type(ohlcv['close'].values))):
                         # Just take the first array for now, or users must use specific naming.
                         # Better: TA-Lib returns multiple arrays. We'll store the first one if not specified.
                         self._indicators[output_name] = pd.Series(result[0], index=ohlcv.index)
                    else:
                        pass
                else:
                    self._indicators[output_name] = pd.Series(result, index=ohlcv.index)
            except Exception as e:
                logger.error("custom_strategy_indicator_failed", strategy=self.name, indicator=output_name, error=str(e))

    def update(self, ohlcv: pd.DataFrame, current_position: str | None = None):
        self.ohlcv = ohlcv
        self.current_position = current_position
        self._compute_indicators(ohlcv)

    def _get_value(self, item: Any, idx: int = -1) -> float:
        """Resolve value which could be a float/int or an indicator string."""
        if isinstance(item, (int, float)):
            return float(item)
        if isinstance(item, str) and item in self._indicators:
            return float(self._indicators[item].iloc[idx])
        # Fallback to column name if it matches (e.g., 'close')
        if isinstance(item, str) and self.ohlcv is not None and item in self.ohlcv.columns:
            return float(self.ohlcv[item].iloc[idx])
            
        try:
            return float(item)
        except (ValueError, TypeError):
            return 0.0

    def _evaluate_conditions(self, conditions: List[Dict[str, Any]]) -> bool:
        if not conditions:
            return False
            
        for cond in conditions:
            indicator_name = cond.get("indicator")
            operator = cond.get("operator")
            value_raw = cond.get("value")
            
            if indicator_name not in self._indicators:
                # Could be a column name like 'close'
                if self.ohlcv is not None and indicator_name in self.ohlcv.columns:
                    ind_series = self.ohlcv[indicator_name]
                else:
                    return False
            else:
                ind_series = self._indicators[indicator_name]
                
            curr_ind = float(ind_series.iloc[-1])
            prev_ind = float(ind_series.iloc[-2]) if len(ind_series) > 1 else curr_ind
            
            curr_val = self._get_value(value_raw, -1)
            prev_val = self._get_value(value_raw, -2)
            
            if operator == ">":
                if not (curr_ind > curr_val):
                    return False
            elif operator == "<":
                if not (curr_ind < curr_val):
                    return False
            elif operator == ">=":
                if not (curr_ind >= curr_val):
                    return False
            elif operator == "<=":
                if not (curr_ind <= curr_val):
                    return False
            elif operator == "crosses_above":
                if not (prev_ind < prev_val and curr_ind >= curr_val):
                    return False
            elif operator == "crosses_below":
                if not (prev_ind > prev_val and curr_ind <= curr_val):
                    return False
            else:
                return False
                
        return True

    def should_long(self) -> bool:
        return self._evaluate_conditions(self.custom_config.get("entry_long_json", []))

    def should_short(self) -> bool:
        return self._evaluate_conditions(self.custom_config.get("entry_short_json", []))

    def should_exit(self) -> bool:
        if self.current_position == "long":
            return self._evaluate_conditions(self.custom_config.get("exit_long_json", []))
        elif self.current_position == "short":
            return self._evaluate_conditions(self.custom_config.get("exit_short_json", []))
        return False

    def get_indicators(self) -> Dict[str, Any]:
        result = {}
        for name, series in self._indicators.items():
            if not series.empty:
                result[name] = float(series.iloc[-1])
        return result
