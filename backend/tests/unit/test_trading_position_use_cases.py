from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.shared.domain.events import EventBus
from src.trading.application.close_position import ClosePositionUseCase
from src.trading.application.open_position import OpenPositionUseCase


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def mock_exchange() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_database() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_risk() -> AsyncMock:
    risk = AsyncMock()
    risk.validate_trade = MagicMock()
    risk.calculate_stop_loss = MagicMock(return_value=99.0)
    risk.calculate_take_profit = MagicMock(return_value=101.0)
    risk.calculate_atr_stops = AsyncMock(return_value=(99.0, 101.0))
    risk.check_circuit_breaker = MagicMock(return_value=False)
    risk.daily_stats = MagicMock()
    risk.daily_stats.realized_pnl = 100.0
    risk.daily_stats.pnl_pct = 2.0
    risk.leverage = 3.0
    return risk


@pytest.mark.asyncio
async def test_open_position_emits_event_on_success(
    event_bus: EventBus,
    mock_exchange: AsyncMock,
    mock_database: AsyncMock,
    mock_risk: AsyncMock,
) -> None:
    """Verify OpenPositionUseCase emits PositionOpened event."""
    use_case = OpenPositionUseCase(
        exchange=mock_exchange,
        database=mock_database,
        risk=mock_risk,
        event_bus=event_bus,
    )

    # Mock validate_trade to return approval
    from src.shared.domain.value_objects import Price, Size
    from src.trading.domain.services.risk_validator import RiskCheck

    risk_check = RiskCheck(
        approved=True,
        reason="Trade approved",
        position_size=Size(0.1),
        stop_loss_price=Price(99.0),
        take_profit_price=Price(101.0),
    )
    mock_risk.validate_trade.return_value = risk_check

    # Mock exchange calls
    mock_exchange.cancel_all_orders = AsyncMock()
    mock_exchange.market_long = AsyncMock(return_value={"id": "order1"})
    mock_exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 100.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )
    mock_exchange.set_stop_loss = AsyncMock()
    mock_exchange.set_take_profit = AsyncMock()

    # Subscribe to events
    events_received = []

    async def capture_event(event):
        events_received.append(event)

    event_bus.subscribe("PositionOpened", capture_event)

    # Execute
    await use_case.execute(
        symbol="BTC/USDT",
        side="long",
        current_price=100.0,
        balance=10000.0,
    )

    # Verify event was emitted
    assert len(events_received) == 1
    assert events_received[0].event_type == "PositionOpened"
    assert events_received[0].payload["symbol"] == "BTC/USDT"
    assert events_received[0].payload["side"] == "long"


@pytest.mark.asyncio
async def test_close_position_emits_event_on_success(
    event_bus: EventBus,
    mock_exchange: AsyncMock,
    mock_database: AsyncMock,
    mock_risk: AsyncMock,
) -> None:
    """Verify ClosePositionUseCase emits PositionClosed event."""
    use_case = ClosePositionUseCase(
        exchange=mock_exchange,
        database=mock_database,
        risk=mock_risk,
        event_bus=event_bus,
    )

    # Mock position
    position = MagicMock()
    position.is_open = True
    position.side = "long"
    position.entry_price = 100.0
    position.size = 0.1

    # Mock exchange calls
    mock_exchange.cancel_all_orders = AsyncMock()
    mock_exchange.close_position = AsyncMock(return_value={"id": "order2"})
    mock_exchange.get_order_fill_details = AsyncMock(
        return_value={
            "average_price": 101.0,
            "total_fee": 1.0,
            "fee_currency": "USDT",
            "confirmed": True,
        }
    )

    # Mock database calls
    mock_database.get_open_trade_fee = AsyncMock(return_value=1.0)

    # Subscribe to events
    events_received = []

    async def capture_event(event):
        events_received.append(event)

    event_bus.subscribe("PositionClosed", capture_event)

    # Execute
    await use_case.execute(
        symbol="BTC/USDT",
        position=position,
        current_price=101.0,
        reason="signal",
    )

    # Verify event was emitted
    assert len(events_received) == 1
    assert events_received[0].event_type == "PositionClosed"
    assert events_received[0].payload["symbol"] == "BTC/USDT"
    assert events_received[0].payload["pnl_pct"] == 1.0
