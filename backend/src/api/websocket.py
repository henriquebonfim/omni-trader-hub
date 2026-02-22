"""
WebSocket live feed.

Broadcasts cycle results (price, signal, indicators, PnL) to all connected clients.
"""

import json
import asyncio
from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger()

router = APIRouter()


class ConnectionManager:
    """Tracks all active WebSocket connections and broadcasts messages."""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)
        logger.info("ws_client_connected", total=len(self._connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections = [ws for ws in self._connections if ws is not websocket]
        logger.info("ws_client_disconnected", total=len(self._connections))

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Send a JSON message to all connected clients, dropping stale ones."""
        if not self._connections:
            return

        message = json.dumps(data, default=str)
        dead: list[WebSocket] = []

        async with self._lock:
            targets = list(self._connections)

        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                self._connections = [ws for ws in self._connections if ws not in dead]

    @property
    def client_count(self) -> int:
        return len(self._connections)


# Singleton manager — assigned to bot.ws_manager in main.py
manager = ConnectionManager()


@router.websocket("/ws/live")
async def live_feed(websocket: WebSocket):
    """Stream every trading cycle result to the connected client."""
    await manager.connect(websocket)
    try:
        # Keep connection alive, waiting for client close
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)
