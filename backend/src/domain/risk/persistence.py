from datetime import date

import structlog

from .models import DailyStats

logger = structlog.get_logger()


class RiskStateStore:
    """Handles state persistence for risk management."""

    def __init__(self, database, bot_id: str = "default"):
        self.database = database
        self._state_key_prefix = f"omnitrader:risk:{bot_id}:"

    async def load_state(self, daily_stats_ref, circuit_breaker_ref, weekly_breaker_ref):
        """Restore state from persistent database."""
        logger.info("risk_manager_restoring_state")
        try:
            # Restore Daily Stats
            daily_stats_data = await self.database.get_state(
                f"{self._state_key_prefix}daily_stats"
            )
            is_same_day = False
            if daily_stats_data:
                stats = DailyStats.from_dict(daily_stats_data)
                # Only restore if it's the same day
                if stats.date == date.today():
                    daily_stats_ref.date = stats.date
                    daily_stats_ref.starting_balance = stats.starting_balance
                    daily_stats_ref.realized_pnl = stats.realized_pnl
                    daily_stats_ref.trades_count = stats.trades_count
                    daily_stats_ref.wins = stats.wins
                    daily_stats_ref.losses = stats.losses
                    is_same_day = True
                    logger.info("restored_daily_stats", stats=daily_stats_data)
                else:
                    logger.info(
                        "skipping_stale_daily_stats", stored_date=str(stats.date)
                    )

            # Restore Consecutive Losses
            losses = await self.database.get_state(
                f"{self._state_key_prefix}consecutive_losses"
            )
            consecutive_losses = int(losses.get("value", 0)) if losses else 0

            # Restore Peak Equity
            peak_eq_data = await self.database.get_state(
                f"{self._state_key_prefix}peak_equity"
            )
            peak_equity = float(peak_eq_data.get("value", 0.0)) if peak_eq_data else 0.0

            # Restore Circuit Breakers
            cb_active = False
            if is_same_day:
                cb_active_data = await self.database.get_state(
                    f"{self._state_key_prefix}circuit_breaker"
                )
                cb_active = bool(cb_active_data.get("value", False)) if cb_active_data else False

            wcb_active_data = await self.database.get_state(
                f"{self._state_key_prefix}weekly_circuit_breaker"
            )
            wcb_active = bool(wcb_active_data.get("value", False)) if wcb_active_data else False

            logger.info("risk_state_restored")
            return consecutive_losses, peak_equity, cb_active, wcb_active

        except Exception as e:
            logger.error("risk_state_restore_failed_critical", error=str(e))
            raise

    async def save_state(self, daily_stats, consecutive_losses, peak_equity, daily_breaker, weekly_breaker):
        """Persist state to database."""
        try:
            await self.database.set_state(
                f"{self._state_key_prefix}daily_stats",
                daily_stats.to_dict(),
                expires_in=86400,
            )
            await self.database.set_state(
                f"{self._state_key_prefix}consecutive_losses",
                {"value": consecutive_losses},
            )
            await self.database.set_state(
                f"{self._state_key_prefix}peak_equity", {"value": peak_equity}
            )
            await self.database.set_state(
                f"{self._state_key_prefix}circuit_breaker",
                {"value": daily_breaker},
            )
            await self.database.set_state(
                f"{self._state_key_prefix}weekly_circuit_breaker",
                {"value": weekly_breaker},
            )
        except Exception as e:
            logger.error("risk_state_save_failed_critical", error=str(e))
            raise
