"""
SMC Multi-Timeframe Analysis.

Coordinating structure analysis across multiple timeframes.
"""


import pandas as pd
import structlog

from .structure import MarketStructure, MarketStructureResult, Trend

logger = structlog.get_logger()


class SMCAnalyzer:
    """
    Coordinator for multi-timeframe SMC analysis.
    """

    def __init__(self, swing_window: int = 5):
        self.structure_analyzer = MarketStructure(swing_window)

    def analyze(
        self, market_data: dict[str, pd.DataFrame]
    ) -> dict[str, MarketStructureResult]:
        """
        Analyze structure for all provided timeframes.

        Args:
            market_data: Dict mapping timeframe (e.g. '1h') to OHLCV DataFrame.

        Returns:
            Dict mapping timeframe to MarketStructureResult.
        """
        results = {}
        for tf, df in market_data.items():
            try:
                if df is None or df.empty:
                    logger.warning("smc_analysis_empty_dataframe", timeframe=tf)
                    continue

                results[tf] = self.structure_analyzer.analyze_structure(df)
            except Exception as e:
                logger.error("smc_analysis_failed", timeframe=tf, error=str(e))

        return results

    def get_bias(
        self, results: dict[str, MarketStructureResult], bias_tf: str = "4h"
    ) -> Trend:
        """Get the trend bias from a higher timeframe."""
        res = results.get(bias_tf)
        if res:
            return res.trend
        return Trend.NEUTRAL
