"""
Discord notification module.

Sends alerts for:
- Trade entries and exits
- Risk warnings
- Errors
- Daily summaries
"""

from datetime import datetime

import httpx
import structlog

from .config import get_config

logger = structlog.get_logger()


class Notifier:
    """
    Discord webhook notifier.

    Sends formatted messages to Discord for trade alerts and system notifications.
    """

    def __init__(self):
        config = get_config()
        self.enabled = config.notifications.enabled
        self.webhook_url = config.notifications.discord_webhook

        if self.enabled and not self.webhook_url:
            logger.warning("discord_webhook_not_configured")
            self.enabled = False

    async def send(self, message: str, title: str = None) -> bool:
        """
        Send a message to Discord.

        Args:
            message: Message content
            title: Optional embed title

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            logger.debug("notification_skipped", reason="disabled")
            return False

        try:
            payload = {"content": message}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url, json=payload, timeout=10.0
                )

                if response.status_code in (200, 204):
                    logger.debug("notification_sent", message=message[:50])
                    return True
                else:
                    logger.warning(
                        "notification_failed",
                        status=response.status_code,
                        response=response.text,
                    )
                    return False

        except Exception as e:
            logger.error("notification_error", error=str(e))
            return False

    async def trade_opened(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        size: float,
        notional: float,
        stop_loss: float,
        take_profit: float,
        leverage: int,
    ):
        """Send trade opened notification."""
        emoji = "🟢" if side == "long" else "🔴"
        side_text = "LONG" if side == "long" else "SHORT"

        sl_pct = abs((stop_loss - entry_price) / entry_price * 100)
        tp_pct = abs((take_profit - entry_price) / entry_price * 100)

        message = f"""
{emoji} **{side_text} OPENED**
```
Symbol:    {symbol}
Entry:     ${entry_price:,.2f}
Size:      {size:.6f} (${notional:,.2f})
Leverage:  {leverage}x
Stop Loss: ${stop_loss:,.2f} (-{sl_pct:.1f}%)
Target:    ${take_profit:,.2f} (+{tp_pct:.1f}%)
```
        """.strip()

        await self.send(message)

    async def trade_closed(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        reason: str = "signal",
    ):
        """Send trade closed notification."""
        emoji = "✅" if pnl >= 0 else "❌"
        side_text = "LONG" if side == "long" else "SHORT"
        pnl_sign = "+" if pnl >= 0 else ""

        message = f"""
{emoji} **POSITION CLOSED**
```
Symbol:  {symbol}
Side:    {side_text}
Entry:   ${entry_price:,.2f}
Exit:    ${exit_price:,.2f}
P/L:     {pnl_sign}${pnl:,.2f} ({pnl_sign}{pnl_pct:.2f}%)
Reason:  {reason}
```
        """.strip()

        await self.send(message)

    async def circuit_breaker(
        self, daily_pnl: float, daily_pnl_pct: float, limit_pct: float
    ):
        """Send circuit breaker notification."""
        message = f"""
⚠️ **CIRCUIT BREAKER TRIGGERED**
```
Daily P/L:  ${daily_pnl:,.2f} ({daily_pnl_pct:.2f}%)
Limit:      -{limit_pct}%
Status:     Trading PAUSED until tomorrow
```
        """.strip()

        await self.send(message)

    async def error(self, error_message: str, context: str = None):
        """Send error notification."""
        message = f"""
🚨 **ERROR**
```
{error_message}
```
        """.strip()

        if context:
            message += f"\nContext: {context}"

        await self.send(message)

    async def bot_started(self, symbol: str, testnet: bool):
        """Send bot started notification."""
        mode = "TESTNET" if testnet else "MAINNET"
        message = f"""
🚀 **OmniTrader Started**
```
Symbol:  {symbol}
Mode:    {mode}
Time:    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
```
        """.strip()

        await self.send(message)

    async def bot_stopped(self, reason: str = "Manual stop"):
        """Send bot stopped notification."""
        message = f"""
🛑 **OmniTrader Stopped**
```
Reason:  {reason}
Time:    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
```
        """.strip()

        await self.send(message)

    async def daily_summary(
        self,
        balance: float,
        daily_pnl: float,
        daily_pnl_pct: float,
        trades_count: int,
        win_rate: float,
    ):
        """Send daily summary notification."""
        emoji = "📈" if daily_pnl >= 0 else "📉"
        pnl_sign = "+" if daily_pnl >= 0 else ""

        message = f"""
{emoji} **Daily Summary**
```
Balance:    ${balance:,.2f}
P/L Today:  {pnl_sign}${daily_pnl:,.2f} ({pnl_sign}{daily_pnl_pct:.2f}%)
Trades:     {trades_count}
Win Rate:   {win_rate:.1f}%
```
        """.strip()

        await self.send(message)

    async def status_update(
        self, balance: float, position: str, price: float, ema_trend: str
    ):
        """Send status update notification."""
        pos_text = position if position else "None"
        trend_emoji = "📈" if ema_trend == "bullish" else "📉"

        message = f"""
📊 **Status Update**
```
Balance:   ${balance:,.2f}
Position:  {pos_text}
BTC Price: ${price:,.2f}
EMA Trend: {trend_emoji} {ema_trend}
```
        """.strip()

        await self.send(message)
