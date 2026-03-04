from enum import Enum

import pandas as pd
import pandas_ta as ta
import structlog

logger = structlog.get_logger()


class MarketRegime(Enum):
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    UNCERTAIN = "uncertain"


class RegimeClassifier:
    """
    Classifies market regime based on technical indicators.

    Logic:
    1. Volatility check: If ATR > 1.5 * SMA(ATR), classify as VOLATILE.
    2. Trend check: If ADX > Threshold (25), classify as TRENDING.
    3. Otherwise: RANGING.
    """

    def __init__(
        self,
        adx_period: int = 14,
        adx_threshold: int = 25,
        atr_period: int = 14,
        atr_multiplier: float = 1.5,
        hysteresis_enabled: bool = False
    ):
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.hysteresis_enabled = hysteresis_enabled
        self.current_regime = MarketRegime.UNCERTAIN

    def analyze(self, ohlcv: pd.DataFrame) -> MarketRegime:
        """
        Analyze OHLCV data to determine market regime.

        Args:
            ohlcv: DataFrame with 'high', 'low', 'close' columns.

        Returns:
            MarketRegime enum.
        """
        if len(ohlcv) < max(self.adx_period, self.atr_period) * 2:
            return MarketRegime.UNCERTAIN

        try:
            # Calculate ADX for Trend Strength
            adx_df = ta.adx(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.adx_period)
            if adx_df is None or adx_df.empty:
                return MarketRegime.UNCERTAIN

            # ADX column name is typically ADX_14
            adx_col = f"ADX_{self.adx_period}"
            if adx_col not in adx_df.columns:
                return MarketRegime.UNCERTAIN

            current_adx = adx_df[adx_col].iloc[-1]

            # Calculate ATR for Volatility
            atr = ta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=self.atr_period)
            if atr is None or atr.empty:
                return MarketRegime.UNCERTAIN

            current_atr = atr.iloc[-1]

            # Calculate SMA of ATR for baseline volatility (use 2x period for smoothing)
            # We need to fillna or handle early NaN values if dataframe is short
            atr_sma = ta.sma(atr, length=self.atr_period * 2)

            if atr_sma is None or atr_sma.empty or pd.isna(atr_sma.iloc[-1]):
                # Fallback: if not enough data for SMA, compare to recent average manually or skip volatility check
                # For safety, if we can't determine volatility baseline, we proceed to ADX check
                avg_atr = current_atr
                is_volatile = False
            else:
                avg_atr = atr_sma.iloc[-1]
                if self.hysteresis_enabled:
                    if self.current_regime == MarketRegime.VOLATILE:
                        is_volatile = current_atr >= (avg_atr * 1.3)
                    else:
                        is_volatile = current_atr > (avg_atr * 1.7)
                else:
                    is_volatile = current_atr > (avg_atr * self.atr_multiplier)

            if self.hysteresis_enabled:
                if self.current_regime == MarketRegime.TRENDING:
                    is_trending = current_adx >= 22
                else:
                    is_trending = current_adx > 28
            else:
                is_trending = current_adx > self.adx_threshold

            # Classification Logic
            if is_volatile:
                self.current_regime = MarketRegime.VOLATILE
            elif is_trending:
                self.current_regime = MarketRegime.TRENDING
            else:
                self.current_regime = MarketRegime.RANGING

            return self.current_regime

        except Exception as e:
            logger.error("regime_classification_failed", error=str(e))
            return MarketRegime.UNCERTAIN
