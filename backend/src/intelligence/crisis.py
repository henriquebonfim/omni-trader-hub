from datetime import datetime, timezone
from typing import Any, Dict

import structlog

from src.database.memgraph import MemgraphDatabase

logger = structlog.get_logger()


class CrisisManager:
    """
    Manages global crisis mode state, persisting it to Memgraph's State nodes.
    Used to gate trading execution when extreme macro events or sentiment crashes are detected.
    """

    CRISIS_STATE_KEY = "global_crisis_mode"

    def __init__(self, database: MemgraphDatabase):
        self.db = database
        self._cached_crisis_state: bool = False
        self._last_check_time: float = 0
        self._cache_ttl: int = 10  # seconds

    async def is_crisis_active(self) -> bool:
        """
        Check if crisis mode is currently active.
        Uses a short TTL cache to prevent hammering Memgraph on every cycle.
        """
        now = datetime.now(timezone.utc).timestamp()

        if now - self._last_check_time < self._cache_ttl:
            return self._cached_crisis_state

        state = await self.db.get_state(self.CRISIS_STATE_KEY)

        if state:
            self._cached_crisis_state = state.get("active", False)
        else:
            self._cached_crisis_state = False

        self._last_check_time = now
        return self._cached_crisis_state

    async def get_crisis_state(self) -> Dict[str, Any]:
        """
        Retrieve full crisis state details.
        """
        state = await self.db.get_state(self.CRISIS_STATE_KEY)
        if state:
            return state
        return {
            "active": False,
            "reason": "Normal operation",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def set_crisis_mode(
        self, active: bool, reason: str = "Manual override"
    ) -> None:
        """
        Enable or disable crisis mode manually via API or automated macro trigger.
        """
        state_val = {
            "active": active,
            "reason": reason,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        await self.db.set_state(self.CRISIS_STATE_KEY, state_val)

        self._cached_crisis_state = active
        self._last_check_time = datetime.now(timezone.utc).timestamp()

        logger.warning("crisis_mode_updated", active=active, reason=reason)

    async def evaluate_automated_crisis(
        self, contagion_risk: bool, sentiment_level: float
    ) -> bool:
        """
        Evaluates graph analytics metrics to trigger automated crisis mode if thresholds are exceeded.
        """
        # Ex: If contagion is active AND overall sentiment is terrible
        if contagion_risk and sentiment_level < -0.8:
            await self.set_crisis_mode(
                True, "Automated contagion and negative sentiment trigger"
            )
            return True

        return False
