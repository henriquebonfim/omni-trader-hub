"""
Watchdog script to monitor OmniTrader health.
Runs alongside the main bot and alerts via Discord if health check fails.

NOTE: This script does NOT restart the bot. It relies on the container/supervisor
(e.g., Docker healthcheck) to restart the process. This script's purpose is to
notify the administrator of the failure.
"""

import os
import time

import httpx
import structlog
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

HEALTH_URL = os.getenv("WATCHDOG_HEALTH_URL", "http://localhost:8000/api/health")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = int(os.getenv("WATCHDOG_INTERVAL", "30"))
MAX_FAILURES = int(os.getenv("WATCHDOG_RETRIES", "3"))


def send_alert(message: str):
    """Send alert to Discord."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("discord_webhook_missing_skipping_alert", message=message)
        return

    try:
        payload = {
            "content": message,
            "username": "OmniTrader Watchdog",
            # "avatar_url": "https://i.imgur.com/4M34hi2.png"
        }
        httpx.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        logger.info("alert_sent_to_discord")
    except Exception as e:
        logger.error("failed_to_send_alert", error=str(e))


def main():
    logger.info("watchdog_started", url=HEALTH_URL, interval=CHECK_INTERVAL)
    failures = 0
    alert_sent = False

    while True:
        try:
            response = httpx.get(HEALTH_URL, timeout=5)
            if response.status_code == 200:
                if failures > 0:
                    logger.info("health_check_recovered", failures=failures)
                    if alert_sent:
                        send_alert("✅ **OmniTrader Recovered**: Health check passing.")
                        alert_sent = False
                failures = 0
            else:
                failures += 1
                logger.warning(
                    "health_check_failed",
                    status=response.status_code,
                    failures=failures,
                )

        except Exception as e:
            failures += 1
            logger.warning("health_check_error", error=str(e), failures=failures)

        if failures >= MAX_FAILURES and not alert_sent:
            msg = f"🚨 **CRITICAL**: OmniTrader health check failed {failures} times! Bot may be down."
            logger.critical("triggering_alert", message=msg)
            send_alert(msg)
            alert_sent = True

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
