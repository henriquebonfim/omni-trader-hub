from dataclasses import dataclass

from src.domain.intelligence.regime import MarketRegime
from src.domain.strategy.base import StrategyResult


@dataclass
class CyclePreflightResult:
    """Cycle preflight snapshot needed by downstream orchestration steps."""

    balance_info: dict
    total_balance: float
    position: object
    current_side: str | None


@dataclass
class CycleAnalysisResult:
    """Cycle analysis output used by persistence, broadcasting, and execution."""

    result: StrategyResult
    current_regime: MarketRegime
    graph_analytics: dict
