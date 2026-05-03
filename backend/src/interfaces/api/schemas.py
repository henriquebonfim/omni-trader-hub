from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ExchangeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Literal["binance"] | None = None
    adapter: Literal["ccxt", "binance_direct"] | None = None
    testnet: bool | None = None
    paper_mode: bool | None = None
    leverage: int | None = Field(None, ge=1, le=125)
    margin_type: Literal["isolated", "cross"] | None = None


class TradingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    symbol: str | None = None
    timeframe: str | None = None
    position_size_pct: float | None = Field(None, gt=0, le=100)
    cycle_seconds: int | None = Field(None, gt=0)


class BollingerBandsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int | None = Field(None, gt=0)
    std: float | None = Field(None, gt=0)
    rsi_length: int | None = Field(None, gt=0)
    rsi_lower: int | None = Field(None, ge=0, le=100)
    rsi_upper: int | None = Field(None, ge=0, le=100)

    @model_validator(mode="after")
    def validate_rsi(self):
        if self.rsi_lower is not None and self.rsi_upper is not None:
            if self.rsi_lower >= self.rsi_upper:
                raise ValueError("rsi_lower must be strictly less than rsi_upper")
        return self


class BreakoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    period: int | None = Field(None, gt=0)


class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["auto", "manual"] | None = None
    name: Literal["ema_volume", "adx_trend", "z_score", "bollinger_bands", "breakout"] | None = None
    ema_fast: int | None = Field(None, gt=0)
    ema_slow: int | None = Field(None, gt=0)
    volume_sma: int | None = Field(None, gt=0)
    volume_threshold: float | None = Field(None, gt=0)
    adx_period: int | None = Field(None, gt=0)
    adx_threshold: int | None = Field(None, gt=0, le=100)
    z_score_window: int | None = Field(None, gt=0)
    z_score_threshold: float | None = Field(None, gt=0)
    bollinger_bands: BollingerBandsConfig | None = None
    breakout: BreakoutConfig | None = None

    @model_validator(mode="after")
    def validate_ema(self):
        if self.ema_fast is not None and self.ema_slow is not None:
            if self.ema_fast >= self.ema_slow:
                raise ValueError("ema_fast must be less than ema_slow")
        return self


class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stop_loss_pct: float | None = Field(None, gt=0, le=100)
    take_profit_pct: float | None = Field(None, gt=0, le=100)
    max_daily_loss_pct: float | None = Field(None, gt=0, le=100)
    max_positions: int | None = Field(None, ge=0)
    trailing_stop_activation_pct: float | None = Field(None, gt=0, le=100)
    trailing_stop_callback_pct: float | None = Field(None, gt=0, le=100)

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
    enabled: bool | None = None
    discord_webhook: HttpUrl | None = None


class ConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    exchange: ExchangeConfig | None = None
    trading: TradingConfig | None = None
    strategy: StrategyConfig | None = None
    risk: RiskConfig | None = None
    notifications: NotificationsConfig | None = None

class StatusResponse(BaseModel):
    running: bool
    running_count: int | None = None
    total_bots: int | None = None
    symbol: str
    paper_mode: bool
    strategy: str
    uptime_seconds: int
    circuit_breaker_active: bool
    ws_clients: int

    # New fields
    last_trade: dict | None = None
    position: dict | None = None
    risk_metrics: dict | None = None
    strategy_indicators: dict | None = None

class MetricsResponse(BaseModel):
    # Trade performance
    win_rate: float
    total_pnl: float
    total_volume: float
    total_trades: int

    # System performance
    cpu_usage_pct: float
    memory_usage_mb: float
    memory_usage_pct: float

    # Exchange connectivity
    exchange_status: str
    exchange_latency_ms: float

    # Error rates
    error_count: int

    # Queue depths
    queue_depths: dict
