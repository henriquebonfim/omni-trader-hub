from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from src.shared.domain.events import EventBus
from src.trading.domain.events import (
    EmergencyClose,
    PositionOpened,
)

if TYPE_CHECKING:
    from src.database.base import BaseDatabase
    from src.exchanges.base import BaseExchange
    from src.risk import RiskManager

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

            notional = risk_check.position_size * entry_price

            # Calculate slippage
            slippage = 0.0
            if side == "long":
                slippage = entry_price - current_price
            else:
                slippage = current_price - entry_price

            # Recalculate or use pre-calculated SL/TP
            stop_loss = risk_check.stop_loss_price
            take_profit = risk_check.take_profit_price

            if use_atr_stops and ohlcv is not None:
                try:
                    stop_loss, take_profit = self.risk.calculate_atr_stops(
                        entry_price, side, ohlcv
                    )
                except Exception as e:
                    logger.warning(f"ATR stops recalculation failed, using fixed: {e}")

            # Set stop loss with retries
            sl_success = False
            for attempt in range(4):
                try:
                    await self.exchange.set_stop_loss(symbol, stop_loss, side)
                    sl_success = True
                    break
                except Exception as e:
                    if attempt < 3:
                        logger.warning(
                            f"Set stop loss failed (attempt {attempt + 1}), retrying: {e}"
                        )
                        await asyncio.sleep(1 * (2**attempt))
                    else:
                        logger.error(f"Set stop loss final failure: {e}")

            if not sl_success:
                logger.critical("Closing position due to SL placement failure")
                pos = await self.exchange.get_position(symbol)
                if pos and pos.is_open:
                    await self.event_bus.publish(
                        EmergencyClose(
                            event_type="EmergencyClose",
                            payload={
                                "symbol": symbol,
                                "reason": "emergency_close_sl_placement_failed",
                            },
                        )
                    )
                return

            # Set take profit with retries
            tp_success = False
            for attempt in range(4):
                try:
                    await self.exchange.set_take_profit(symbol, take_profit, side)
                    tp_success = True
                    break
                except Exception as e:
                    if attempt < 3:
                        logger.warning(
                            f"Set take profit failed (attempt {attempt + 1}), retrying: {e}"
                        )
                        await asyncio.sleep(1 * (2**attempt))
                    else:
                        logger.error(f"Set take profit final failure: {e}")

            if not tp_success:
                logger.critical("Closing position due to TP placement failure")
                pos = await self.exchange.get_position(symbol)
                if pos and pos.is_open:
                    await self.event_bus.publish(
                        EmergencyClose(
                            event_type="EmergencyClose",
                            payload={
                                "symbol": symbol,
                                "reason": "emergency_close_tp_placement_failed",
                            },
                        )
                    )
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
            )

            # Emit domain event (notifications handled by subscribers)
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
                        "leverage": getattr(self.risk, "leverage", 1),
                    },
                )
            )

            logger.info(
                f"Position opened: {symbol} {side} @ {entry_price} size={risk_check.position_size} SL={stop_loss} TP={take_profit}"
            )

        except Exception as e:
            logger.error(f"Open position failed: {e}")
            raise
