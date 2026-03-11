import asyncio
import uuid
import structlog
from typing import Dict, List, Optional
from src.main import OmniTrader
from src.config import get_config, Config
from src.database.factory import DatabaseFactory

logger = structlog.get_logger()


class BotManager:
    """
    Orchestrates multiple OmniTrader bot instances and persists their definitions.
    """
    def __init__(self, database=None):
        self._global_config = get_config()
        self.database = database or DatabaseFactory.get_database(self._global_config)
        self.bots: Dict[str, OmniTrader] = {}
        self._state_key = "omnitrader:bot_manager:configs"
        
    async def load_bots(self):
        """Load bot configurations from Memgraph and initialize them."""
        logger.info("loading_bot_manager_state")
        
        saved_configs = await self.database.get_state(self._state_key)
        if saved_configs and "bots" in saved_configs:
            for bot_id, bot_conf_dict in saved_configs["bots"].items():
                logger.info("restoring_bot", bot_id=bot_id, symbol=bot_conf_dict.get("trading", {}).get("symbol"))
                try:
                    bot = self._create_bot_instance(bot_id, bot_conf_dict)
                    self.bots[bot_id] = bot
                except Exception as e:
                    logger.error("failed_to_restore_bot", bot_id=bot_id, error=str(e))
        else:
            # First time initialization: adopt the default bot
            logger.info("initializing_default_bot")
            bot_id = "default"
            bot_conf_dict = self._global_config.to_dict()
            bot = self._create_bot_instance(bot_id, bot_conf_dict)
            self.bots[bot_id] = bot
            await self._save_state()

    def _create_bot_instance(self, bot_id: str, config_dict: dict) -> OmniTrader:
        """Create a new OmniTrader instance with the given config dict."""
        # Deep merge with global config to ensure missing keys are present
        merged_dict = self._merge_dicts(self._global_config.to_dict(), config_dict)
        bot_config = Config(merged_dict)
        
        # We pass bot_id into OmniTrader so it uses isolated risk state prefix
        bot = OmniTrader(bot_id=bot_id, config=bot_config)
        return bot

    def _merge_dicts(self, d1: dict, d2: dict) -> dict:
        """Deep merge d2 into d1."""
        merged = dict(d1)
        for k, v in d2.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self._merge_dicts(merged[k], v)
            else:
                merged[k] = v
        return merged

    async def _save_state(self):
        """Persist all bot configurations to Memgraph."""
        bots_data = {}
        for bot_id, bot in self.bots.items():
            bots_data[bot_id] = bot.config.to_dict()
            
        try:
            await self.database.set_state(self._state_key, {"bots": bots_data})
        except Exception as e:
            logger.error("failed_to_save_bot_manager_state", error=str(e))

    def get_bot(self, bot_id: str) -> Optional[OmniTrader]:
        return self.bots.get(bot_id)

    def list_bots(self) -> List[dict]:
        return [
            {
                "id": bot_id, 
                "symbol": bot.config.trading.symbol, 
                "timeframe": bot.config.trading.timeframe,
                "strategy": getattr(bot.config.strategy, "name", "unknown"),
                "paper_mode": getattr(bot.config.exchange, "paper_mode", True),
                "running": bot._running
            } 
            for bot_id, bot in self.bots.items()
        ]

    async def create_bot(self, config_overrides: dict) -> str:
        """Create a new bot with the given config overrides and save state."""
        bot_id = str(uuid.uuid4())
        
        # Build new config based on global
        merged_dict = self._merge_dicts(self._global_config.to_dict(), config_overrides)
        
        bot = self._create_bot_instance(bot_id, merged_dict)
        
        self.bots[bot_id] = bot
        await self._save_state()
        
        logger.info("bot_created", bot_id=bot_id, symbol=bot.config.trading.symbol)
        return bot_id

    async def update_bot(self, bot_id: str, config_overrides: dict) -> bool:
        """Update a bot's configuration."""
        if bot_id not in self.bots:
            return False
            
        bot = self.bots[bot_id]
        if bot._running:
            raise ValueError("Cannot update configuration while bot is running")
            
        current_dict = bot.config.to_dict()
        merged_dict = self._merge_dicts(current_dict, config_overrides)
        
        new_bot = self._create_bot_instance(bot_id, merged_dict)
        self.bots[bot_id] = new_bot
        
        await self._save_state()
        logger.info("bot_updated", bot_id=bot_id, symbol=new_bot.config.trading.symbol)
        return True

    async def delete_bot(self, bot_id: str) -> bool:
        """Delete a bot. Ensure it's stopped first."""
        if bot_id not in self.bots:
            return False
            
        bot = self.bots[bot_id]
        if bot._running:
            await self.stop_bot(bot_id)
            
        del self.bots[bot_id]
        await self._save_state()
        
        logger.info("bot_deleted", bot_id=bot_id)
        return True
        
    async def start_bot(self, bot_id: str) -> bool:
        """Start a bot's trading loop. Returns False if already running."""
        bot = self.bots.get(bot_id)
        if not bot or bot._running:
            return False
        await bot.start()
        logger.info("bot_started", bot_id=bot_id)
        return True

    async def stop_bot(self, bot_id: str, reason: str = "api_stop") -> bool:
        """Stop a bot's trading loop. Returns False if not running."""
        bot = self.bots.get(bot_id)
        if not bot or not bot._running:
            return False
        await bot.stop(reason)
        logger.info("bot_stopped", bot_id=bot_id, reason=reason)
        return True

    async def stop_all(self):
        """Stop all running bots gracefully."""
        tasks = []
        for bot_id, bot in self.bots.items():
            if bot._running:
                tasks.append(bot.stop("manager_shutdown"))
        if tasks:
            await asyncio.gather(*tasks)
