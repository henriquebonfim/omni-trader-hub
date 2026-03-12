"""
Celery application for OmniTrader.

Uses the existing Redis container as broker (DB 1) and result backend (DB 2),
keeping DB 0 free for the Anti-Amnesia persistence layer.

Usage::

    # Start a worker (from /app inside the container):
    celery -A src.workers worker --loglevel=info --concurrency=2

    # Or via docker compose (see compose.yml celery-worker service).
"""

import os
from datetime import timedelta

from celery import Celery

_REDIS_HOST = os.getenv("REDIS_HOST", "redis")
_REDIS_PORT = os.getenv("REDIS_PORT", "6379")
_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

_auth = f":{_REDIS_PASSWORD}@" if _REDIS_PASSWORD else ""

BROKER_URL = f"redis://{_auth}{_REDIS_HOST}:{_REDIS_PORT}/1"
RESULT_BACKEND_URL = f"redis://{_auth}{_REDIS_HOST}:{_REDIS_PORT}/2"

celery_app = Celery(
    "omnitrader",
    broker=BROKER_URL,
    backend=RESULT_BACKEND_URL,
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Reliability
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    # Result expiry — 5 minutes is more than enough for a trading cycle
    result_expires=300,
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Periodic scheduling
    beat_schedule={
        "ingest-news-hourly": {
            "task": "omnitrader.ingest_news_cycle",
            "schedule": timedelta(hours=1),
        }
    },
)
