import pandas as pd
import structlog

logger = structlog.get_logger()


class MarketWatchdog:
    """Detects black swans and liquidation risks."""

    def __init__(self, config):
        self.config = config

    def check_black_swan(self, ohlcv: pd.DataFrame) -> bool:
        """Detect extreme market moves (>10% move in last hour)."""
        if ohlcv is None or ohlcv.empty:
            return False

        try:
            last_timestamp = ohlcv.index[-1]
            one_hour_ago = last_timestamp - pd.Timedelta(hours=1)
            recent_data = ohlcv[ohlcv.index >= one_hour_ago]

            if recent_data.empty:
                return False

            high_max = recent_data["high"].max()
            low_min = recent_data["low"].min()

            if low_min <= 0:
                return False

            volatility_pct = (high_max - low_min) / low_min
            if volatility_pct > 0.10:
                logger.critical(
                    "black_swan_detected",
                    volatility_pct=f"{volatility_pct:.2%}",
                    high=high_max,
                    low=low_min,
                )
                return True
        except Exception:
            logger.exception("black_swan_check_failed")
            return True  # Fail-safe

        return False

    def check_liquidation_risk(self, position, current_price: float) -> bool:
        """Check if position is too close to liquidation price."""
        if not hasattr(position, "is_open") or not position.is_open:
            return False
        if not hasattr(position, "liquidation_price") or position.liquidation_price <= 0:
            return False

        dist_to_liq = abs(current_price - position.liquidation_price)
        total_dist = abs(position.entry_price - position.liquidation_price)

        if total_dist == 0:
            return False

        remaining_pct = dist_to_liq / total_dist
        if remaining_pct < self.config.risk.liquidation_buffer_pct:
            logger.warning(
                "liquidation_risk_critical",
                symbol=position.symbol,
                remaining_pct=f"{remaining_pct:.2%}",
            )
            return True

        return False
