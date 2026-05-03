from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.domain.shared.events import EventBus
from src.domain.trading.events import CircuitBreakerTriggered, PositionClosed

if TYPE_CHECKING:
    from src.infrastructure.database.base import BaseDatabase
    from src.infrastructure.exchanges.base import BaseExchange, Position
    from src.domain.risk import RiskManager

logger = logging.getLogger(__name__)


class ClosePositionUseCase:
    """Use case: close a position with risk updates and event emission."""

    def __init__(
        self,
        exchange: BaseExchange,
        database: BaseDatabase,
        risk: RiskManager,
        event_bus: EventBus,
    ) -> None:
        self.exchange = exchange
        self.database = database
        self.risk = risk
        self.event_bus = event_bus

    async def execute(
        self,
        symbol: str,
        position: Position,
        current_price: float,
        reason: str = "signal",
    ) -> None:
        """
        Close a position with risk recording and event emission.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            position: Current position object
            current_price: Market price at decision time
            reason: Reason for closing (e.g., 'signal', 'stop_loss', 'emergency')
        """
        if not position.is_open:
            logger.warning("No position to close")
            return

        expected_price = current_price

        try:
            # Cancel any existing orders
            await self.exchange.cancel_all_orders(symbol)

            # Close position
            close_result = self.exchange.close_position(symbol)
            if hasattr(close_result, "__await__"):
                order = await close_result
            else:
                order = close_result

            if order is None:
                return

            # Verify fills and get actual price/fees
            fill_details = await self.exchange.get_order_fill_details(
                order["id"], symbol
            )
            exit_price = float(
                fill_details["average_price"]
                or order.get("average")
                or order.get("price")
                or current_price
            )
            total_fee = fill_details["total_fee"]
            fee_currency = fill_details["fee_currency"]

            # Calculate slippage
            slippage = 0.0
            if position.side == "long":
                slippage = expected_price - exit_price
            else:
                slippage = exit_price - expected_price

            # Calculate PnL
            if position.side == "long":
                pnl = (exit_price - position.entry_price) * position.size
                pnl_pct = (
                    (exit_price - position.entry_price) / position.entry_price
                ) * 100
            else:
                pnl = (position.entry_price - exit_price) * position.size
                pnl_pct = (
                    (position.entry_price - exit_price) / position.entry_price
                ) * 100

            # Fetch opening trade fees
            open_fee = await self.database.get_open_trade_fee(symbol)
            net_pnl = pnl - total_fee - open_fee

            # Record in risk manager
            risk_result = self.risk.record_trade(net_pnl)
            if hasattr(risk_result, "__await__"):
                await risk_result

            # Log to database
            db_result = self.database.log_trade_close(
                symbol=symbol,
                side=position.side,
                price=exit_price,
                size=position.size,
                notional=position.size * exit_price,
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason=reason,
                expected_price=expected_price,
                slippage=slippage,
                fee=total_fee,
                fee_currency=fee_currency,
            )
            if hasattr(db_result, "__await__"):
                await db_result

            # Emit domain event (notifications handled by subscribers)
            await self.event_bus.publish(
                PositionClosed(
                    event_type="PositionClosed",
                    payload={
                        "symbol": symbol,
                        "side": position.side,
                        "entry_price": position.entry_price,
                        "exit_price": exit_price,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "reason": reason,
                    },
                )
            )

            # Check if circuit breaker triggered and emit event
            if self.risk.check_circuit_breaker():
                await self.event_bus.publish(
                    CircuitBreakerTriggered(
                        event_type="CircuitBreakerTriggered",
                        payload={
                            "daily_pnl": self.risk.daily_stats.realized_pnl,
                            "daily_pnl_pct": self.risk.daily_stats.pnl_pct,
                            "limit_pct": self.risk.max_daily_loss_pct,
                        },
                    )
                )

            logger.info(
                f"Position closed: {symbol} {position.side} @{position.entry_price}→{exit_price} PnL=${pnl:.2f} ({pnl_pct:.2f}%)"
            )

        except Exception as e:
            logger.error(f"Close position failed: {e}")
            raise
