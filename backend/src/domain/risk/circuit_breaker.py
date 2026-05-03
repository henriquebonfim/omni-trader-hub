import structlog

logger = structlog.get_logger()


class CircuitBreaker:
    """Manages daily and weekly circuit breakers."""

    def __init__(self, config):
        self.config = config

    def check_daily_breaker(self, pnl_pct: float) -> bool:
        """Check if daily loss limit exceeded."""
        if pnl_pct <= -self.config.risk.max_daily_loss_pct:
            logger.warning(
                "circuit_breaker_triggered",
                daily_pnl_pct=f"{pnl_pct:.2f}%",
                limit=f"-{self.config.risk.max_daily_loss_pct}%",
            )
            return True
        return False

    def check_weekly_breaker(self, weekly_pnl: float, current_balance: float) -> bool:
        """Check if weekly loss limit exceeded."""
        start_week_balance = current_balance - weekly_pnl
        if start_week_balance <= 0:
            return False

        weekly_pnl_pct = (weekly_pnl / start_week_balance) * 100
        if weekly_pnl_pct <= -self.config.risk.max_weekly_loss_pct:
            logger.warning(
                "weekly_circuit_breaker_triggered",
                weekly_pnl=weekly_pnl,
                weekly_pnl_pct=f"{weekly_pnl_pct:.2f}%",
                limit=f"-{self.config.risk.max_weekly_loss_pct}%",
            )
            return True
        return False
