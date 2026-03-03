"""
Async dispatcher — bridges Celery's synchronous `.get()` into asyncio.

Running `AsyncResult.get()` inside an `async def` would block the event loop.
Instead, we push the blocking call into a `ThreadPoolExecutor` so the loop
stays free for I/O (heartbeats, API requests) while the worker crunches.

Usage::

    from src.workers.dispatch import dispatch

    result_dict = await dispatch(
        analyze_strategy,
        strategy_name, config_dict, market_data_json, current_side
    )
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

# Shared executor — 2 threads is sufficient; we only ever run 2 Celery tasks
# in parallel per cycle (strategy + regime).
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="celery-dispatch")


async def dispatch(task, *args, timeout: float = 30.0, **kwargs) -> Any:
    """
    Dispatch a Celery task and await its result without blocking the event loop.

    Parameters
    ----------
    task:
        A Celery task object (from ``src.workers.tasks``).
    *args:
        Positional arguments forwarded to the task.
    timeout:
        Seconds to wait for the worker result before raising ``TimeoutError``.
    **kwargs:
        Keyword arguments forwarded to the task.

    Returns
    -------
    Any
        The task return value.

    Raises
    ------
    TimeoutError
        If the worker does not respond within *timeout* seconds.
    celery.exceptions.TaskError
        If the task itself raises an exception.
    """
    loop = asyncio.get_event_loop()

    def _run():
        async_result = task.apply_async(args=args, kwargs=kwargs)
        return async_result.get(timeout=timeout, propagate=True)

    return await loop.run_in_executor(_executor, _run)
