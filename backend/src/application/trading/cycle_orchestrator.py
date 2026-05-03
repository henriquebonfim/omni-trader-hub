import asyncio
from datetime import UTC, date, datetime, timedelta
from typing import Any

import structlog

from src.domain.intelligence.regime import MarketRegime
from src.domain.strategy import Signal
from src.domain.strategy.base import StrategyResult
from src.domain.trading.types import CycleAnalysisResult, CyclePreflightResult
from src.interfaces.workers.serializers import df_to_json, market_data_to_json
from src.interfaces.workers.tasks import analyze_knowledge_graph, analyze_regime, analyze_strategy

from .market_data_fetcher import MarketDataFetcher

logger = structlog.get_logger()


class CycleOrchestrator:
    """
    Coordinates a single trading cycle for the OmniTrader bot.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.market_data_fetcher = MarketDataFetcher(
            exchange=bot.exchange,
            ws_feed=bot.ws_feed,
            config=self.config,
            notifier=bot.notifier,
        )

    async def _cycle_preflight(self, symbol: str) -> CyclePreflightResult | None:
        if self.bot.risk.check_circuit_breaker():
            logger.warning("circuit_breaker_active", status="skipping_cycle")
            return None

        balance_info = await self.bot.exchange.get_balance()
        total_balance = balance_info["total"]

        self.bot._weekly_check_counter += 1
        if self.bot._weekly_check_counter >= 60:
            self.bot._weekly_check_counter = 0
            try:
                today = date.today()
                start_of_week = today - timedelta(days=6)
                weekly_pnl = await self.bot.database.get_weekly_pnl(
                    start_of_week.isoformat()
                )
                if await self.bot.risk.check_weekly_circuit_breaker(
                    weekly_pnl, total_balance
                ):
                    logger.critical(
                        "weekly_circuit_breaker_active", status="skipping_cycle"
                    )
                    await self.bot.notifier.send(
                        "🚨 **Weekly Circuit Breaker Triggered**! Trading paused."
                    )
                    return None
            except Exception as e:
                logger.error("weekly_circuit_breaker_check_failed", error=str(e))

        if self.bot.risk._weekly_circuit_breaker_active:
            logger.warning("weekly_circuit_breaker_active", status="skipping_cycle")
            return None

        position = await self.bot.exchange.get_position(symbol)
        current_side = position.side if position.is_open else None

        self.bot._reconcile_counter += 1
        if self.bot._reconcile_counter >= 5:
            await self.bot.reconciler.reconcile(symbol, position)
            self.bot._reconcile_counter = 0

        self.bot._funding_check_counter += 1
        if self.bot._funding_check_counter >= 60:
            self.bot._funding_check_counter = 0
            funding_rate = await self.bot.exchange.fetch_funding_rate(symbol)
            if abs(funding_rate) > 0.0003:
                logger.warning("high_funding_rate", rate=funding_rate)
                await self.bot.notifier.send(
                    f"⚠️ **High Funding Rate**: {funding_rate * 100:.4f}% for {symbol}"
                )
            if position.is_open:
                payment = position.notional * funding_rate
                cost = payment if position.side == "long" else -payment
                await self.bot.database.log_funding_payment(
                    symbol=symbol,
                    rate=funding_rate,
                    payment=cost,
                    position_size=position.size,
                )

        await self.bot.risk.initialize_daily_stats(total_balance)
        return CyclePreflightResult(
            balance_info=balance_info,
            total_balance=total_balance,
            position=position,
            current_side=current_side,
        )

    async def _handle_black_swan(
        self, symbol: str, primary_ohlcv, position, current_price: float
    ) -> bool:
        if not self.bot.risk.check_black_swan(primary_ohlcv):
            return False

        try:
            if position.is_open:
                logger.critical("black_swan_flattening_positions")
                await self.bot._close_position(
                    position=position,
                    current_price=current_price,
                    reason="black_swan_emergency_exit",
                )
        except Exception as e:
            logger.error("black_swan_close_failed", error=str(e))

        await self.bot.notifier.send(
            "🚨 **BLACK SWAN DETECTED**: >10% move in 1h. Positions flattened. Bot stopping."
        )
        await self.bot.stop("Black Swan Event")
        return True

    async def _analyze_cycle(
        self, symbol: str, market_data, primary_ohlcv, current_price: float, current_side, market_trend: str
    ):
        strategy_mode = getattr(self.config.strategy, "mode", "manual")

        regime_value = MarketRegime.TRENDING.value
        primary_ohlcv_json = df_to_json(primary_ohlcv)
        try:
            regime_value_result = await self.bot.dispatch(
                analyze_regime,
                primary_ohlcv_json,
                timeout=25.0,
            )
            if not isinstance(regime_value_result, Exception):
                regime_value = regime_value_result
        except Exception as e:
            logger.warning("regime_analysis_failed_fallback_to_trending", error=str(e))
            current_regime_fallback = self.bot.regime_classifier.analyze(primary_ohlcv)
            regime_value = current_regime_fallback.value

        current_regime = MarketRegime(regime_value)

        if self.bot._last_regime and self.bot._last_regime != current_regime.value:
            await self.bot._emit_ws_alert(
                "info",
                "Regime Change",
                f"{symbol} shifted from {self.bot._last_regime.upper()} to {current_regime.value.upper()}.",
                rule_key="regime_change",
            )
        self.bot._last_regime = current_regime.value

        if strategy_mode == "auto":
            await self.bot.strategy_manager.rotate_if_needed(current_regime)

        strategy_name = getattr(self.config.strategy, "name", "ema_volume")
        config_dict = self.bot._config_dict()
        market_data_json = market_data_to_json(market_data)

        try:
            results = await asyncio.gather(
                self.bot.dispatch(
                    analyze_strategy,
                    strategy_name,
                    config_dict,
                    market_data_json,
                    current_side,
                    market_trend,
                    timeout=25.0,
                ),
                self.bot.dispatch(
                    analyze_knowledge_graph,
                    symbol,
                    current_price,
                    config_dict,
                    timeout=25.0,
                ),
                return_exceptions=True,
            )
            strategy_result_dict: Any = results[0]
            graph_analytics_dict: Any = results[1]

            if isinstance(strategy_result_dict, Exception):
                raise strategy_result_dict

            result = StrategyResult(
                signal=Signal(strategy_result_dict["signal"]),
                reason=strategy_result_dict["reason"],
                indicators=strategy_result_dict["indicators"],
            )
            graph_analytics = (
                graph_analytics_dict
                if not isinstance(graph_analytics_dict, Exception)
                else {}
            )
        except Exception as celery_exc:
            logger.warning(
                "celery_dispatch_failed_using_local_fallback",
                error=str(celery_exc),
            )
            result = self.bot.strategy.analyze(
                market_data, current_side, market_trend=market_trend
            )
            graph_analytics = {}

        if graph_analytics:
            contagion_risk = graph_analytics.get("contagion", {}).get(
                "contagion_risk", False
            )
            sentiment_level = graph_analytics.get("sentiment", {}).get(
                "avg_sentiment", 0.0
            )
            await self.bot.crisis_manager.evaluate_automated_crisis(
                contagion_risk, sentiment_level
            )

        is_crisis = await self.bot.crisis_manager.is_crisis_active()
        if is_crisis:
            if result.signal in (Signal.LONG, Signal.SHORT) and not current_side:
                logger.warning(
                    "signal_rejected_crisis_mode",
                    signal=result.signal,
                    reason="Crisis Mode Active",
                )
                result.signal = Signal.HOLD
                result.reason = "Crisis Mode Active"
        elif current_regime not in self.bot.strategy.valid_regimes:
            if result.signal in (Signal.LONG, Signal.SHORT) and not current_side:
                logger.warning(
                    "signal_rejected_regime_mismatch",
                    signal=result.signal,
                    regime=current_regime.value,
                    valid_regimes=[r.value for r in self.bot.strategy.valid_regimes],
                )
                result.signal = Signal.HOLD
                result.reason = f"Regime Mismatch: {current_regime.value}"

        return CycleAnalysisResult(
            result=result,
            current_regime=current_regime,
            graph_analytics=graph_analytics,
        )

    async def _persist_and_broadcast_cycle(
        self, symbol: str, current_price: float, result: StrategyResult,
        current_regime: MarketRegime, market_trend: str, current_side,
        balance_total: float, graph_analytics
    ):
        sanitized_indicators = self.bot._sanitize_indicators(result.indicators)

        logger.info(
            "cycle_analyzed",
            price=f"${current_price:,.2f}",
            signal=result.signal.value,
            position=current_side or "none",
            reason=result.reason,
            **sanitized_indicators,
        )

        await self.bot.database.log_equity_snapshot(balance_total)
        signal_id = await self.bot.database.log_signal(
            symbol=symbol,
            price=current_price,
            signal=result.signal.value,
            regime=current_regime.value,
            reason=result.reason,
            strategy_name=getattr(self.config.strategy, "name", ""),
            indicators=sanitized_indicators,
        )

        if result.signal in (Signal.LONG, Signal.SHORT) and not current_side:
            side = "long" if result.signal == Signal.LONG else "short"
            await self.bot._open_position(
                side, current_price, balance_total, reason=result.reason, signal_id=signal_id
            )
        elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT) and current_side:
            from src.infrastructure.exchanges.base import Position
            fake_pos = Position({"symbol": symbol, "side": current_side})
            await self.bot._close_position(fake_pos, current_price, reason=result.reason)

        time_in_trade_s = 0.0
        if current_side:
            try:
                last_trade = await self.bot.database.get_last_trade(symbol)
                if last_trade and last_trade["action"] == "OPEN":
                    entry_dt = datetime.fromisoformat(last_trade["timestamp"])
                    if entry_dt.tzinfo is None:
                        entry_dt = entry_dt.replace(tzinfo=UTC)
                    now_dt = datetime.now(UTC)
                    time_in_trade_s = max(0, (now_dt - entry_dt).total_seconds())
            except Exception as e:
                logger.warning("time_in_trade_calc_failed", error=str(e))

        if self.bot.ws_manager:
            await self.bot.ws_manager.broadcast(
                {
                    "type": "cycle_update",
                    "bot_id": "default",
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "price": current_price,
                    "signal": result.signal.value,
                    "regime": current_regime.value,
                    "reason": result.reason,
                    "market_trend": market_trend,
                    "indicators": sanitized_indicators,
                    "position": current_side,
                    "time_in_trade": time_in_trade_s,
                    "balance": balance_total,
                    "daily_pnl": self.bot.risk.daily_stats.realized_pnl,
                    "daily_pnl_pct": self.bot.risk.daily_stats.pnl_pct,
                    "circuit_breaker": self.bot.risk.check_circuit_breaker(),
                    "graph_analytics": graph_analytics,
                }
            )

    async def _manage_open_position(self, symbol: str, position, current_price: float) -> bool:
        if not position.is_open:
            return False

        if self.bot.risk.check_liquidation_risk(position, current_price):
            await self.bot._close_position(
                position, current_price, reason="liquidation_risk_exit"
            )
            await self.bot.notifier.send(
                f"🚨 **URGENT**: Position closed due to liquidation risk! Price: {current_price}, Liq: {position.liquidation_price}"
            )
            return True

        open_orders = await self.bot.exchange.fetch_open_orders(symbol)
        current_stop_price = None
        for order in open_orders:
            if order.get("type") == "stop_market" or order.get("type") == "STOP_MARKET":
                current_stop_price = float(
                    order.get("stopPrice") or order.get("triggerPrice") or 0
                )
                break

        new_stop = self.bot.risk.calculate_trailing_stop(current_price, position)
        if not new_stop:
            return False

        should_update = False
        if current_stop_price is None or position.side == "long" and new_stop > current_stop_price or position.side == "short" and new_stop < current_stop_price:
            should_update = True

        if should_update:
            logger.info(
                "trailing_stop_update",
                symbol=symbol,
                current_stop=current_stop_price,
                new_stop=new_stop,
            )
            try:
                await self.bot.exchange.set_stop_loss(symbol, new_stop, position.side)
            except Exception as e:
                logger.error("trailing_stop_update_failed", error=str(e))

        return False

    async def _execute_signal(
        self, symbol: str, result: StrategyResult, position, current_price: float, free_balance: float, primary_ohlcv
    ):
        if result.signal == Signal.LONG:
            await self.bot._open_position(
                "long",
                current_price,
                free_balance,
                reason=result.reason,
                ohlcv=primary_ohlcv,
            )
        elif result.signal == Signal.SHORT:
            await self.bot._open_position(
                "short",
                current_price,
                free_balance,
                reason=result.reason,
                ohlcv=primary_ohlcv,
            )
        elif result.signal in (Signal.EXIT_LONG, Signal.EXIT_SHORT):
            await self.bot._close_position(position, current_price, reason=result.reason)

    async def run_cycle(self):
        """Execute one trading cycle."""
        symbol = self.config.trading.symbol

        try:
            preflight = await self._cycle_preflight(symbol)
            if preflight is None:
                return
            balance_info = preflight.balance_info
            total_balance = preflight.total_balance
            position = preflight.position
            current_side = preflight.current_side

            self.bot._last_position = position
            self.bot._last_balance = total_balance

            market_context = await self.market_data_fetcher.fetch_market_context(
                symbol, self.bot.strategy
            )
            if market_context is None:
                return
            market_data, primary_ohlcv, current_price, market_trend = market_context

            should_stop = await self._handle_black_swan(
                symbol=symbol,
                primary_ohlcv=primary_ohlcv,
                position=position,
                current_price=current_price,
            )
            if should_stop:
                return

            analysis = await self._analyze_cycle(
                symbol=symbol,
                market_data=market_data,
                primary_ohlcv=primary_ohlcv,
                current_price=current_price,
                current_side=current_side,
                market_trend=market_trend,
            )

            await self._persist_and_broadcast_cycle(
                symbol=symbol,
                current_price=current_price,
                result=analysis.result,
                current_regime=analysis.current_regime,
                market_trend=market_trend,
                current_side=current_side,
                balance_total=total_balance,
                graph_analytics=analysis.graph_analytics,
            )

            should_stop = await self._manage_open_position(
                symbol, position, current_price
            )
            if should_stop:
                return

            await self._execute_signal(
                symbol=symbol,
                result=analysis.result,
                position=position,
                current_price=current_price,
                free_balance=balance_info["free"],
                primary_ohlcv=primary_ohlcv,
            )

        except Exception as e:
            logger.error("cycle_error", error=str(e))
            await self.bot.notifier.error(str(e), "run_cycle")

