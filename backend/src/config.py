"""
Configuration management for OmniTrader MVP.

Loads configuration from YAML file with environment variable substitution.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Configuration container with dot-notation access."""

    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def __repr__(self) -> str:
        return f"Config({vars(self)})"

    def to_dict(self) -> dict:
        """Convert config back to dictionary."""
        result = {}
        for key, value in vars(self).items():
            if isinstance(value, Config):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result


def _substitute_env_vars(value: Any) -> Any:
    """Replace ${VAR} patterns with environment variable values."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        return os.getenv(env_var, "")
    return value


def _process_config(data: dict) -> dict:
    """Recursively process config and substitute env vars."""
    result = {}
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
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to config/config.yaml

    Returns:
        Config object with dot-notation access
    """
    if config_path is None:
        # Default to config/config.yaml relative to project root
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "config.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    # Process environment variable substitution
    processed_config = _process_config(raw_config)

    return Config(processed_config)


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
