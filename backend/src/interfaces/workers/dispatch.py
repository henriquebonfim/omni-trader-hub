"""
Async dispatcher — bridges Celery's synchronous `.get()` into asyncio.

Running `AsyncResult.get()` inside an `async def` would block the event loop.
Instead, we push the blocking call into a `ThreadPoolExecutor` so the loop
stays free for I/O (heartbeats, API requests) while the worker crunches.

Includes Circuit Breaker pattern: if Celery worker is unresponsive (3+ consecutive
failures), bypass Celery entirely for 5 minutes to avoid ThreadPoolExecutor starvation.

Usage::

    from src.interfaces.workers.dispatch import dispatch

    result_dict = await dispatch(
        analyze_strategy,
        strategy_name, config_dict, market_data_json, current_side
    )
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import structlog

logger = structlog.get_logger()

# Shared executor — 4 threads; Celery dispatch is blocking.
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="celery-dispatch")

# Circuit breaker state
_failure_count = 0
_last_failure_time = None
_circuit_open_until = None
_FAILURE_THRESHOLD = 3  # Trips breaker after 3 consecutive failures
_CIRCUIT_OPEN_DURATION = 300  # Stay open for 5 minutes (300 seconds)


async def dispatch(task, *args, timeout: float = 30.0, **kwargs) -> Any:
    """
    Dispatch a Celery task and await its result without blocking the event loop.

    Implements Circuit Breaker pattern: if Celery worker is unresponsive, falls back
    to local task execution after 3 consecutive failures.

    Parameters
    ----------
    task:
        A Celery task object (from ``src.interfaces.workers.tasks``).
    *args:
        Positional arguments forwarded to the task.
    timeout:
        Seconds to wait for the worker result before raising ``TimeoutError``.
    **kwargs:
        Keyword arguments forwarded to the task.

    Returns
    -------
    Any
        The task return value (from Celery worker or local fallback).

    Raises
    ------
    TimeoutError
        If the worker does not respond within *timeout* seconds.
    celery.exceptions.TaskError
        If the task itself raises an exception.
    """
    global _failure_count, _last_failure_time, _circuit_open_until

    # Check if circuit breaker should close (5 minutes elapsed)
    if _circuit_open_until is not None and time.time() >= _circuit_open_until:
        logger.warning("celery_circuit_breaker_closed", timeout_expired=True)
        _circuit_open_until = None
        _failure_count = 0

    # If circuit is open, use local fallback
    if _circuit_open_until is not None:
        logger.warning(
            "celery_circuit_breaker_open",
            reason="Celery worker unresponsive",
            fallback="local_execution",
            remaining_seconds=int(_circuit_open_until - time.time()),
        )
        # Fallback: run task synchronously (no asyncio yield, but non-blocking alternative)
        return await _run_local_fallback(task, *args, **kwargs)

    # Try Celery dispatch
    loop = asyncio.get_event_loop()

    def _run():
        async_result = task.apply_async(args=args, kwargs=kwargs)
        return async_result.get(timeout=timeout, propagate=True)

    try:
        result = await loop.run_in_executor(_executor, _run)
        # Success: reset failure counter
        _failure_count = 0
        _last_failure_time = None
        return result
    except Exception as e:
        _failure_count += 1
        _last_failure_time = time.time()

        if _failure_count >= _FAILURE_THRESHOLD:
            # Trip circuit breaker
            _circuit_open_until = time.time() + _CIRCUIT_OPEN_DURATION
            logger.error(
                "celery_circuit_breaker_tripped",
                failure_count=_failure_count,
                error=str(e),
                circuit_open_for_seconds=_CIRCUIT_OPEN_DURATION,
            )
            # Fall back to local execution instead of failing
            return await _run_local_fallback(task, *args, **kwargs)
        else:
            logger.warning(
                "celery_dispatch_failed",
                attempt=_failure_count,
                threshold=_FAILURE_THRESHOLD,
                error=str(e),
            )
            raise


async def _run_local_fallback(task, *args, **kwargs) -> Any:
    """
    Fallback when Celery worker is unavailable.
    Executes task logic synchronously in a thread pool to avoid blocking event loop.
    """
    loop = asyncio.get_event_loop()

    def _run_task():
        # Call the task function directly without Celery
        return task.run(*args, **kwargs)

    try:
        return await loop.run_in_executor(_executor, _run_task)
    except Exception as e:
        logger.error("celery_fallback_failed", error=str(e), task_name=task.name)
        raise
