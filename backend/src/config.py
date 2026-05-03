import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# Load .env file
load_dotenv()


class TradingConfig(BaseModel):
    symbol: str = "BTC/USDT:USDT"
    timeframe: str = "15m"
    fee_rate: float = 0.0
    position_size_pct: float = 2.0
    cycle_seconds: int = 60
    ohlcv_limit: int = 100


class BollingerBandsConfig(BaseModel):
    length: int = 20
    std: float = 2.0
    rsi_length: int = 14
    rsi_lower: int = 30
    rsi_upper: int = 70


class BreakoutConfig(BaseModel):
    period: int = 20


class ADXConfig(BaseModel):
    period: int = 14
    threshold: int = 25


class ZScoreConfig(BaseModel):
    window: int = 20
    threshold: float = 2.0


class StrategyConfig(BaseModel):
    name: str = "ema_volume"
    mode: str = "manual"
    ema_fast: int = 9
    ema_slow: int = 21
    volume_sma: int = 20
    volume_threshold: float = 1.5
    trend_filter_enabled: bool = False
    trend_timeframe: str = "4h"
    bias_confirmation: bool = True
    bias_timeframe: str = "4h"
    bollinger_bands: BollingerBandsConfig = Field(default_factory=BollingerBandsConfig)
    breakout: BreakoutConfig = Field(default_factory=BreakoutConfig)
    adx: ADXConfig = Field(default_factory=ADXConfig)
    z_score: ZScoreConfig = Field(default_factory=ZScoreConfig)

    model_config = ConfigDict(extra="allow")


class RiskConfig(BaseModel):
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0
    use_atr_stops: bool = True
    atr_period: int = 14
    atr_multiplier_sl: float = 1.5
    atr_multiplier_tp: float = 2.0
    stop_loss_atr_mult: float = 0.0
    take_profit_atr_mult: float = 0.0
    max_daily_loss_pct: float = 5.0
    max_weekly_loss_pct: float = 10.0
    max_positions: int = 1
    liquidation_buffer_pct: float = 0.5
    trailing_stop_activation_pct: float = 1.0
    trailing_stop_callback_pct: float = 0.5
    reconciliation_lookback_trades: int = 50


class ExchangeConfig(BaseModel):
    paper_mode: bool = True
    leverage: int = 3
    margin_type: str = "isolated"
    adapter: str = "ccxt"
    testnet: bool = False


class DatabaseConfig(BaseModel):
    type: str = "memgraph"
    host: str = os.getenv("MEMGRAPH_HOST", "memgraph")
    port: int = int(os.getenv("MEMGRAPH_PORT", "7687"))
    encrypted: bool = os.getenv("MEMGRAPH_ENCRYPTED", "false").lower() == "true"
    username: str = os.getenv("MEMGRAPH_USERNAME", "")
    password: str = os.getenv("MEMGRAPH_PASSWORD", "")


class RedisConfig(BaseModel):
    host: str = os.getenv("REDIS_HOST", "redis")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "1"))


class GraphConfig(BaseModel):
    cryptocompare_api_key: str = os.getenv("CRYPTOCOMPARE_API_KEY", "")


class IntelligenceConfig(BaseModel):
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
    generation_timeout: float = 120.0


class BacktestConfig(BaseModel):
    slippage_bps: float = 2.0
    spread_bps: float = 1.0


class NotificationsConfig(BaseModel):
    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    enabled: bool = True
    alert_rules: dict[str, Any] = Field(default_factory=lambda: {
        "circuit_breaker": True,
        "strategy_rotation": True,
        "regime_change": True,
        "pnl_thresholds": True,
        "pnl_warning_pct": 3.0,
        "pnl_critical_pct": 5.0
    })

    @property
    def discord_webhook(self) -> str:
        return self.discord_webhook_url


class Config(BaseModel):
    """Configuration container with explicit typing and dot-notation access."""

    trading: TradingConfig = Field(default_factory=TradingConfig)
    strategy: StrategyConfig = Field(default_factory=StrategyConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    exchange: ExchangeConfig = Field(default_factory=ExchangeConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    graph: GraphConfig = Field(default_factory=GraphConfig)
    intelligence: IntelligenceConfig = Field(default_factory=IntelligenceConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)

    # Legacy compatibility: allow positional dict for tests or earlier call sites.
    def __init__(self, *args, **kwargs):
        if args:
            if len(args) == 1 and isinstance(args[0], dict):
                kwargs = args[0]
            else:
                raise TypeError("Config.__init__ accepts only one positional dict argument")
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Convert config back to dictionary."""
        return self.model_dump()


def _substitute_env_vars(value: Any) -> Any:
    """Replace ${VAR} patterns with environment variable values."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        return os.getenv(env_var, "")
    return value


def _process_config(data: dict) -> dict:
    """Recursively process config and substitute env vars."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _process_config(value)
        elif isinstance(value, list):
            result[key] = [_substitute_env_vars(item) for item in value]
        else:
            result[key] = _substitute_env_vars(value)
    return result


def load_config(config_path: str | Path | None = None) -> Config:
    """
    Load configuration. Defaults to Pydantic/Env defaults if no file is provided or found.

    Args:
        config_path: Optional path to config file.

    Returns:
        Config object with explicit typing
    """
    if config_path is None:
        # Default to config/config.yaml relative to project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "config.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        # Return default config if file is missing (intended for DB-only setup)
        return Config()

    try:
        with open(config_path) as f:
            raw_config = yaml.safe_load(f) or {}

        # Process environment variable substitution
        processed_config = _process_config(raw_config)

        # Map to typed Config structure
        return Config.model_validate(processed_config)
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.warning("failed_to_load_config_file", path=str(config_path), error=str(e))
        return Config()


async def load_config_from_db(database: Any) -> Config:
    """
    Load global configuration from database.
    
    Args:
        database: Database implementation with get_state support.
    """
    state_key = "omnitrader:global_config"
    try:
        data = await database.get_state(state_key)
        if data:
            return Config.model_validate(data)
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("failed_to_load_config_from_db", error=str(e))
    
    return get_config()


async def save_config_to_db(database: Any, config: Config) -> None:
    """
    Save global configuration to database.
    """
    state_key = "omnitrader:global_config"
    try:
        await database.set_state(state_key, config.to_dict())
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("failed_to_save_config_to_db", error=str(e))


# Default config instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global config instance, loading if necessary."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Config:
    """Force reload of configuration."""
    global _config
    _config = load_config()
    return _config
