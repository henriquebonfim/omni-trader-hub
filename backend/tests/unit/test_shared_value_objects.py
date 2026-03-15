import pytest

from src.shared.domain.value_objects import Leverage, Percentage, PnL, Price, Side, Size


def test_side_enum_values() -> None:
    assert Side.LONG.value == "long"
    assert Side.SHORT.value == "short"


def test_price_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Price(0)
    with pytest.raises(ValueError):
        Price(-1)


def test_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Size(0)
    with pytest.raises(ValueError):
        Size(-0.01)


def test_leverage_bounds() -> None:
    assert float(Leverage(1)) == 1
    assert float(Leverage(125)) == 125

    with pytest.raises(ValueError):
        Leverage(0.9)
    with pytest.raises(ValueError):
        Leverage(126)


def test_percentage_bounds() -> None:
    assert float(Percentage(0)) == 0
    assert float(Percentage(100)) == 100

    with pytest.raises(ValueError):
        Percentage(-0.1)
    with pytest.raises(ValueError):
        Percentage(100.1)


def test_pnl_allows_signed_values() -> None:
    assert float(PnL(-10.5)) == -10.5
    assert float(PnL(42.0)) == 42.0
