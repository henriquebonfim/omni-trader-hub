from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from src.domain.shared.events import EventBus
from src.domain.trading.events import (
    EmergencyClose,
    FillUnconfirmed,
    PositionOpened,
)

if TYPE_CHECKING:
    from src.infrastructure.database.base import BaseDatabase
    from src.infrastructure.exchanges.base import BaseExchange
    from src.domain.risk import RiskManager

logger = logging.getLogger(__name__)


class OpenPositionUseCase:
    """Use case: open a position with risk validation and event emission."""

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
        side: str,
        current_price: float,
        balance: float,
        ohlcv=None,
        reason: str = "signal",
        use_atr_stops: bool = False,
        signal_id: str | None = None,
    ) -> None:
        """
        Open a position with full risk validation and event emission.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: Position side ('long' or 'short')
            current_price: Market price at decision time
            balance: Available account balance
            ohlcv: OHLCV DataFrame for ATR calculation (optional)
            reason: Reason for opening (e.g., 'signal', 'manual')
            use_atr_stops: Whether to calculate SL/TP using ATR
            signal_id: ID of the triggering signal (optional)
        """
        # Fetch current positions count from exchange
        try:
            open_positions = await self.exchange.get_open_positions()
            current_positions_count = len(open_positions)
        except Exception as e:
            logger.error(f"Failed to fetch open positions: {e}")
            return

        # Validate with risk manager
        risk_check = self.risk.validate_trade(
            side=side,
            balance=balance,
            entry_price=current_price,
            symbol=symbol,
            exchange=self.exchange,
            current_positions=current_positions_count,
            ohlcv=ohlcv,
        )

        if not risk_check.approved:
            logger.warning(f"Trade rejected: {risk_check.reason}")
            return

        try:
            # Cancel any existing orders
            await self.exchange.cancel_all_orders(symbol)

            # Place market order
            if side == "long":
                order = await self.exchange.market_long(
                    symbol, risk_check.position_size
                )
            else:
                order = await self.exchange.market_short(
                    symbol, risk_check.position_size
                )

            # Verify fills and get actual price/fees
            fill_details = await self.exchange.get_order_fill_details(
                order["id"], symbol
            )
            entry_price = float(
                fill_details["average_price"] or order.get("average", current_price)
            )
            total_fee = fill_details["total_fee"]
            fee_currency = fill_details["fee_currency"]

            if not fill_details.get("confirmed", True):
                # Log unconfirmed fills both for main logger tests and event stream
                try:
                    from src.main import logger as main_logger

                    main_logger.warning(
                        "order_fill_not_confirmed",
                        order_id=order["id"],
                        symbol=symbol,
                    )
                except Exception:
                    logger.warning(
                        "order_fill_not_confirmed",
                        order_id=order["id"],
                        symbol=symbol,
                    )

                await self.event_bus.publish(
                    FillUnconfirmed(
                        event_type="FillUnconfirmed",
                        payload={"order_id": order["id"], "symbol": symbol},
                    )
                )

            notional = risk_check.position_size * entry_price

            # Calculate slippage
            slippage = entry_price - current_price if side == "long" else current_price - entry_price

            # Use risk check prices if available, otherwise calculate
            stop_loss = risk_check.stop_loss_price
            take_profit = risk_check.take_profit_price

            if stop_loss == 0 or take_profit == 0:
                if use_atr_stops and ohlcv is not None:
                    try:
                        stop_loss, take_profit = self.risk.calculate_atr_stops(entry_price, side, ohlcv)
                    except Exception as e:
                        logger.warning(f"ATR stops recalculation failed, using fixed: {e}")
                        stop_loss = self.risk.calculate_stop_loss(entry_price, side)
                        take_profit = self.risk.calculate_take_profit(entry_price, side)
                else:
                    stop_loss = self.risk.calculate_stop_loss(entry_price, side)
                    take_profit = self.risk.calculate_take_profit(entry_price, side)

            # Set protection orders with retries
            sl_success = await self._set_protection_order(symbol, stop_loss, side, "stop_loss")
            if not sl_success:
                await self._emergency_close(symbol, entry_price, "emergency_close_sl_placement_failed")
                return

            tp_success = await self._set_protection_order(symbol, take_profit, side, "take_profit")
            if not tp_success:
                await self._emergency_close(symbol, entry_price, "emergency_close_tp_placement_failed")
                return

            # Log to database
            await self.database.log_trade_open(
                symbol=symbol,
                side=side,
                price=entry_price,
                size=risk_check.position_size,
                notional=notional,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reason=reason,
                expected_price=current_price,
                slippage=slippage,
                fee=total_fee,
                fee_currency=fee_currency,
                signal_id=signal_id,
            )

            # Emit domain event
            await self.event_bus.publish(
                PositionOpened(
                    event_type="PositionOpened",
                    payload={
                        "symbol": symbol,
                        "side": side,
                        "entry_price": entry_price,
                        "size": float(risk_check.position_size),
                        "notional": notional,
                        "stop_loss": float(stop_loss),
                        "take_profit": float(take_profit),
                        "leverage": self.risk.config.exchange.leverage,
                    },
                )
            )

            logger.info(
                f"Position opened: {symbol} {side} @ {entry_price} size={risk_check.position_size} SL={stop_loss} TP={take_profit}"
            )

        except Exception as e:
            logger.error(f"Open position failed: {e}")
            raise

    async def _set_protection_order(self, symbol: str, price: float, side: str, order_type: str) -> bool:
        """Set SL or TP order with retries."""
        for attempt in range(4):
            try:
                if order_type == "stop_loss":
                    await self.exchange.set_stop_loss(symbol, price, side)
                else:
                    await self.exchange.set_take_profit(symbol, price, side)
                return True
            except Exception as e:
                if attempt < 3:
                    logger.warning(f"Set {order_type} failed (attempt {attempt + 1}), retrying: {e}")
                    await asyncio.sleep(1 * (2**attempt))
                else:
                    logger.error(f"Set {order_type} final failure: {e}")
        return False

    async def _emergency_close(self, symbol: str, entry_price: float, reason: str):
        """Handle emergency position closure when protection orders fail."""
        logger.critical(f"EMERGENCY_FLATTEN_TRIGGERED: {reason}", symbol=symbol)
        
        try:
            # Actually close the position on the exchange
            order = await self.exchange.close_position(symbol)
            
            # Get current position info for the event
            pos = await self.exchange.get_position(symbol)
            
            await self.event_bus.publish(
                EmergencyClose(
                    event_type="EmergencyClose",
                    payload={
                        "symbol": symbol,
                        "order": order,
                        "position": pos.to_dict() if pos else None,
                        "reason": reason,
                        "entry_price": entry_price,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )
            )
            
            from src.infrastructure.notifier import Notifier
            notifier = Notifier()
            await notifier.send(f"🚨 **EMERGENCY FLATTEN**: {symbol} closed due to {reason}!")
            
        except Exception as e:
            logger.error(f"EMERGENCY_FLATTEN_FAILED: {e}", symbol=symbol)
            # If even closing fails, we are in deep trouble
            raise

