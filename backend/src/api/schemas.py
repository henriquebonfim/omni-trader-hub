from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ExchangeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[Literal["binance"]] = None
    adapter: Optional[Literal["ccxt", "binance_direct"]] = None
    testnet: Optional[bool] = None
    paper_mode: Optional[bool] = None
    leverage: Optional[int] = Field(None, ge=1, le=125)
    margin_type: Optional[Literal["isolated", "cross"]] = None


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

    @model_validator(mode="after")
    def validate_rsi(self):
        if self.rsi_lower is not None and self.rsi_upper is not None:
            if self.rsi_lower >= self.rsi_upper:
                raise ValueError("rsi_lower must be strictly less than rsi_upper")
        return self


class BreakoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period: Optional[int] = Field(None, gt=0)


class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[
        Literal["ema_volume", "adx_trend", "z_score", "bollinger_bands", "breakout"]
    ] = None
    ema_fast: Optional[int] = Field(None, gt=0)
    ema_slow: Optional[int] = Field(None, gt=0)
    volume_sma: Optional[int] = Field(None, gt=0)
    volume_threshold: Optional[float] = Field(None, gt=0)
    adx_period: Optional[int] = Field(None, gt=0)
    adx_threshold: Optional[int] = Field(None, gt=0, le=100)
    z_score_window: Optional[int] = Field(None, gt=0)
    z_score_threshold: Optional[float] = Field(None, gt=0)
    bollinger_bands: Optional[BollingerBandsConfig] = None
    breakout: Optional[BreakoutConfig] = None

    @model_validator(mode="after")
    def validate_ema(self):
        if self.ema_fast is not None and self.ema_slow is not None:
            if self.ema_fast >= self.ema_slow:
                raise ValueError("ema_fast must be less than ema_slow")
        return self


class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stop_loss_pct: Optional[float] = Field(None, gt=0, le=100)
    take_profit_pct: Optional[float] = Field(None, gt=0, le=100)
    max_daily_loss_pct: Optional[float] = Field(None, gt=0, le=100)
    max_positions: Optional[int] = Field(None, ge=0)
    trailing_stop_activation_pct: Optional[float] = Field(None, gt=0, le=100)
    trailing_stop_callback_pct: Optional[float] = Field(None, gt=0, le=100)

    @model_validator(mode="after")
    def validate_trailing_stop(self):
        if (
            self.trailing_stop_activation_pct is not None
            and self.trailing_stop_callback_pct is not None
        ):
            if self.trailing_stop_activation_pct <= self.trailing_stop_callback_pct:
                raise ValueError("activation_pct must be greater than callback_pct")
        return self


class NotificationsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: Optional[bool] = None
    discord_webhook: Optional[HttpUrl] = None


class ConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exchange: Optional[ExchangeConfig] = None
    trading: Optional[TradingConfig] = None
    strategy: Optional[StrategyConfig] = None
    risk: Optional[RiskConfig] = None
    notifications: Optional[NotificationsConfig] = None
