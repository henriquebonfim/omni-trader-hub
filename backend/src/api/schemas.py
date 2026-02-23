from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExchangeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    testnet: Optional[bool] = None
    paper_mode: Optional[bool] = None
    leverage: Optional[int] = Field(None, ge=1)
    margin_type: Optional[str] = None

class TradingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    position_size_pct: Optional[float] = Field(None, gt=0, le=100)
    cycle_seconds: Optional[int] = Field(None, gt=0)

class BollingerBandsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: Optional[int] = Field(None, gt=0)
    std: Optional[float] = Field(None, gt=0)
    rsi_length: Optional[int] = Field(None, gt=0)
    rsi_lower: Optional[int] = Field(None, ge=0, le=100)
    rsi_upper: Optional[int] = Field(None, ge=0, le=100)

class BreakoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period: Optional[int] = Field(None, gt=0)

class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    ema_fast: Optional[int] = Field(None, gt=0)
    ema_slow: Optional[int] = Field(None, gt=0)
    volume_sma: Optional[int] = Field(None, gt=0)
    volume_threshold: Optional[float] = Field(None, gt=0)
    adx_period: Optional[int] = Field(None, gt=0)
    adx_threshold: Optional[int] = Field(None, gt=0)
    z_score_window: Optional[int] = Field(None, gt=0)
    z_score_threshold: Optional[float] = Field(None, gt=0)
    bollinger_bands: Optional[BollingerBandsConfig] = None
    breakout: Optional[BreakoutConfig] = None

class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stop_loss_pct: Optional[float] = Field(None, gt=0)
    take_profit_pct: Optional[float] = Field(None, gt=0)
    max_daily_loss_pct: Optional[float] = Field(None, gt=0)
    max_positions: Optional[int] = Field(None, ge=0)
    trailing_stop_activation_pct: Optional[float] = Field(None, gt=0)
    trailing_stop_callback_pct: Optional[float] = Field(None, gt=0)

class NotificationsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: Optional[bool] = None
    discord_webhook: Optional[str] = None

class ConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exchange: Optional[ExchangeConfig] = None
    trading: Optional[TradingConfig] = None
    strategy: Optional[StrategyConfig] = None
    risk: Optional[RiskConfig] = None
    notifications: Optional[NotificationsConfig] = None
