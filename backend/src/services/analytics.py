import numpy as np
from typing import List, Dict, Any

class PerformanceCalculator:
    """Utility class to calculate trading performance metrics."""

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate the annualized Sharpe Ratio.
        Assumes returns are from daily cycles (approx 365 per year for crypto).
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        avg_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        # Annualization factor for crypto (365 days)
        # If returns are per cycle, we might need a different factor.
        # Assuming 1 return per day for simplicity now.
        sharpe = (avg_return - risk_free_rate) / std_return
        return float(sharpe * np.sqrt(365))

    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """Calculate the maximum drawdown from an equity curve."""
        if not equity_curve:
            return 0.0
        
        equity = np.array(equity_curve)
        peak = np.maximum.accumulate(equity)
        # Avoid division by zero
        peak[peak == 0] = 1e-9
        
        drawdown = (equity - peak) / peak
        return float(np.min(drawdown))

    @staticmethod
    def calculate_profit_factor(gross_profits: List[float], gross_losses: List[float]) -> float:
        """Calculate the profit factor (Gross Profit / Gross Loss)."""
        total_profit = sum(gross_profits)
        total_loss = abs(sum(gross_losses))
        
        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0.0
        
        return float(total_profit / total_loss)

    @staticmethod
    def calculate_win_rate(win_count: int, loss_count: int) -> float:
        """Calculate win rate percentage."""
        total = win_count + loss_count
        if total == 0:
            return 0.0
        return float(win_count / total)
