from enum import Enum

import pandas as pd
import structlog

from src.domain import indicators

# Backward-compatible alias for tests and older modules that still patch/use `ta.*`.
ta = indicators

logger = structlog.get_logger()


class MarketRegime(Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    UNCERTAIN = "uncertain"


class RegimeClassifier:
    """Classifies market regime based on ADX/ATR indicators."""

    MIN_DATA_MULTIPLIER = 2
    HYSTERESIS_TREND_ENTRY = 28
    HYSTERESIS_TREND_EXIT = 22
    HYSTERESIS_VOLATILE_ENTRY = 1.7
    HYSTERESIS_VOLATILE_EXIT = 1.3

    def __init__(
        self,
        adx_period: int = 14,
        adx_threshold: int = 25,
        atr_period: int = 14,
        atr_multiplier: float = 1.5,
        hysteresis_enabled: bool = False,
        indicators_module=ta,
    ):
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.hysteresis_enabled = hysteresis_enabled
        self.current_regime = MarketRegime.UNCERTAIN
        self.indicators = indicators_module

    def analyze(self, ohlcv: pd.DataFrame) -> MarketRegime:
        if not self._has_sufficient_data(ohlcv):
            return MarketRegime.UNCERTAIN

        try:
            current_adx = self._get_current_adx(ohlcv)
            if current_adx is None:
                return MarketRegime.UNCERTAIN

            current_atr = self._get_current_atr(ohlcv)
            if current_atr is None:
                return MarketRegime.UNCERTAIN

            atr_baseline = self._get_atr_baseline(ohlcv)

            volatile = self._is_volatile(current_atr, atr_baseline)
            trending = self._is_trending(current_adx)

            next_regime = self._classify(volatile, trending)
            self.current_regime = next_regime
            return next_regime

        except Exception as e:
            logger.error("regime_classification_failed", error=str(e))
            return MarketRegime.UNCERTAIN

    def _has_sufficient_data(self, ohlcv: pd.DataFrame) -> bool:
        min_rows = max(self.adx_period, self.atr_period) * self.MIN_DATA_MULTIPLIER
        return len(ohlcv) >= min_rows

    def _get_current_adx(self, ohlcv: pd.DataFrame) -> float | None:
        adx_df = self.indicators.adx(
            ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.adx_period
        )
        if not isinstance(adx_df, pd.DataFrame) or adx_df.empty:
            return None

        adx_col = f"ADX_{self.adx_period}"
        if adx_col not in adx_df.columns or pd.isna(adx_df[adx_col].iloc[-1]):
            return None

        return float(adx_df[adx_col].iloc[-1])

    def _get_current_atr(self, ohlcv: pd.DataFrame) -> float | None:
        atr = self.indicators.atr(
            ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.atr_period
        )
        if not isinstance(atr, (pd.Series, pd.DataFrame)) or atr.empty:
            return None

        current_atr = atr.iloc[-1]
        return float(current_atr) if not pd.isna(current_atr) else None

    def _get_atr_baseline(self, ohlcv: pd.DataFrame) -> float | None:
        atr = self.indicators.atr(
            ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.atr_period
        )
        if not isinstance(atr, (pd.Series, pd.DataFrame)) or atr.empty:
            return None

        atr_sma = self.indicators.sma(atr, length=self.atr_period * self.MIN_DATA_MULTIPLIER)
        if not isinstance(atr_sma, (pd.Series, pd.DataFrame)) or atr_sma.empty:
            return None

        latest = atr_sma.iloc[-1]
        return float(latest) if not pd.isna(latest) else None

    def _is_volatile(self, current_atr: float, atr_baseline: float | None) -> bool:
        if atr_baseline is None or atr_baseline <= 0:
            return False

        if self.hysteresis_enabled:
            if self.current_regime == MarketRegime.VOLATILE:
                threshold = self.HYSTERESIS_VOLATILE_EXIT
            else:
                threshold = self.HYSTERESIS_VOLATILE_ENTRY
            return current_atr >= atr_baseline * threshold

        return current_atr > atr_baseline * self.atr_multiplier

    def _is_trending(self, current_adx: float) -> bool:
        if self.hysteresis_enabled:
            if self.current_regime == MarketRegime.TRENDING:
                return current_adx >= self.HYSTERESIS_TREND_EXIT
            return current_adx > self.HYSTERESIS_TREND_ENTRY

        return current_adx > self.adx_threshold

    def _classify(self, is_volatile: bool, is_trending: bool) -> MarketRegime:
        if is_volatile:
            return MarketRegime.VOLATILE
        if is_trending:
            return MarketRegime.TRENDING
        return MarketRegime.RANGING
