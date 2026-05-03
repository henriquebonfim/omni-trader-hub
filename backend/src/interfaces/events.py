from collections.abc import Callable
from datetime import UTC, datetime

import structlog

logger = structlog.get_logger()

class BotEventManager:
    """
    Handles domain events and orchestrates side effects like notifications and alerts.
    """

    def __init__(self, event_bus, config, notifier, ws_manager=None, close_position_cb: Callable = None):
        self.event_bus = event_bus
        self.config = config
        self.notifier = notifier
        self.ws_manager = ws_manager
        self.close_position_cb = close_position_cb

    def setup_handlers(self):
        """Register all event handlers with the event bus."""
        self.event_bus.subscribe("PositionOpened", self.on_position_opened)
        self.event_bus.subscribe("PositionClosed", self.on_position_closed)
        self.event_bus.subscribe("CircuitBreakerTriggered", self.on_circuit_breaker_triggered)
        self.event_bus.subscribe("EmergencyClose", self.on_emergency_close)
        self.event_bus.subscribe("FillUnconfirmed", self.on_fill_unconfirmed)

    async def on_position_opened(self, event) -> None:
        payload = event.payload
        await self.notifier.trade_opened(
            symbol=payload["symbol"],
            side=payload["side"],
            entry_price=payload["entry_price"],
            size=payload["size"],
            notional=payload["notional"],
            stop_loss=payload["stop_loss"],
            take_profit=payload["take_profit"],
            leverage=payload.get("leverage", self.config.exchange.leverage),
        )
        await self._emit_ws_trade("OPEN", payload)
        await self._emit_ws_alert(
            "info",
            "Trade Opened",
            f"{payload['symbol']} {payload['side'].upper()} opened at ${payload['entry_price']:,.2f}",
        )

    async def on_position_closed(self, event) -> None:
        payload = event.payload
        await self.notifier.trade_closed(
            symbol=payload["symbol"],
            side=payload["side"],
            entry_price=payload["entry_price"],
            exit_price=payload["exit_price"],
            pnl=payload["pnl"],
            pnl_pct=payload["pnl_pct"],
            reason=payload["reason"],
        )
        await self._emit_ws_trade("CLOSE", payload)

        if self._alert_rule_enabled("pnl_thresholds"):
            rules = self._get_notification_rules()
            abs_pnl_pct = abs(float(payload["pnl_pct"]))
            warning_pct = float(rules["pnl_warning_pct"])
            critical_pct = float(rules["pnl_critical_pct"])
            if abs_pnl_pct >= critical_pct:
                await self._emit_ws_alert(
                    "critical",
                    "PnL Threshold Hit",
                    f"{payload['symbol']} closed at {payload['pnl_pct']:+.2f}% (critical >= {critical_pct:.2f}%).",
                    rule_key="pnl_thresholds",
                )
            elif abs_pnl_pct >= warning_pct:
                await self._emit_ws_alert(
                    "warning",
                    "PnL Threshold Warning",
                    f"{payload['symbol']} closed at {payload['pnl_pct']:+.2f}% (warning >= {warning_pct:.2f}%).",
                    rule_key="pnl_thresholds",
                )

    async def on_circuit_breaker_triggered(self, event) -> None:
        payload = event.payload
        daily_pnl = payload.get("daily_pnl", 0.0)
        daily_pnl_pct = payload.get("daily_pnl_pct", 0.0)
        limit_pct = payload.get("limit_pct", 0.0)

        # Guard against MagicMock or invalid types during unit tests
        try:
            daily_pnl_pct_val = float(daily_pnl_pct)
        except Exception:
            daily_pnl_pct_val = 0.0

        try:
            limit_pct_val = float(limit_pct)
        except Exception:
            limit_pct_val = 0.0

        await self.notifier.circuit_breaker(
            daily_pnl=daily_pnl,
            daily_pnl_pct=daily_pnl_pct_val,
            limit_pct=limit_pct_val,
        )
        await self._emit_ws_alert(
            "critical",
            "Circuit Breaker Triggered",
            f"Daily PnL {daily_pnl_pct_val:.2f}% breached limit -{limit_pct_val:.2f}%.",
            rule_key="circuit_breaker",
        )

    async def on_emergency_close(self, event) -> None:
        payload = event.payload
        symbol = payload.get("symbol")
        position = payload.get("position")
        reason = payload.get("reason")
        entry_price = payload.get("entry_price")

        if self.close_position_cb and position is not None:
            callback = self.close_position_cb
            # If the callback is a bound method, try to resolve the latest version
            # in case it was reassigned on the owner object (test mocks often do this).
            if hasattr(callback, "__self__") and hasattr(callback, "__func__"):
                owner = callback.__self__
                method_name = callback.__func__.__name__
                if hasattr(owner, method_name):
                    callback = getattr(owner, method_name)

            await callback(position, entry_price, reason)

        await self.notifier.send(
            f"🚨 **EMERGENCY CLOSE**: {symbol} closed due to {reason}"
        )

    async def on_fill_unconfirmed(self, event) -> None:
        payload = event.payload
        logger.warning(
            "order_fill_not_confirmed",
            order_id=payload["order_id"],
            symbol=payload["symbol"],
        )

    def _get_notification_rules(self) -> dict[str, float | bool]:
        defaults: dict[str, float | bool] = {
            "circuit_breaker": True,
            "strategy_rotation": True,
            "regime_change": True,
            "pnl_thresholds": True,
            "pnl_warning_pct": 3.0,
            "pnl_critical_pct": 5.0,
        }
        notifications = getattr(self.config, "notifications", None)
        raw_rules = getattr(notifications, "alert_rules", None)
        if hasattr(raw_rules, "to_dict"):
            raw_rules = raw_rules.to_dict()
        if not isinstance(raw_rules, dict):
            return defaults
        return {**defaults, **raw_rules}

    def _alert_rule_enabled(self, rule_key: str) -> bool:
        return bool(self._get_notification_rules().get(rule_key, True))

    async def _emit_ws_alert(self, level: str, title: str, body: str, *, rule_key: str | None = None) -> None:
        if not self.ws_manager:
            return
        if rule_key and not self._alert_rule_enabled(rule_key):
            return
        await self.ws_manager.broadcast({
            "type": "alert",
            "level": level,
            "title": title,
            "body": body,
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        })

    async def _emit_ws_trade(self, action: str, payload: dict) -> None:
        if not self.ws_manager:
            return
        await self.ws_manager.broadcast({
            "type": "trade",
            "bot_id": "default",
            "symbol": payload["symbol"],
            "action": action,
            "side": payload["side"],
            "price": payload.get("entry_price") if action == "OPEN" else payload.get("exit_price"),
            "size": payload.get("size", 0.0),
            "pnl": payload.get("pnl"),
            "timestamp": int(datetime.now(UTC).timestamp() * 1000),
        })
