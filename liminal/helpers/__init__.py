"""Define helpers."""

import asyncio
from collections.abc import Awaitable
from typing import Any


def run_sync(coro: Awaitable) -> Any:  # noqa: ANN401
    """Run an async coroutine synchronously.

    Args:
    ----
        coro: The coroutine to run.
        loop: The event loop to use (defaulting to the running one).

    Returns:
    -------
        The result of the coroutine.

    """
    loop = asyncio.get_event_loop()

    # If the event loop is already running, use a thread-safe mechanism:
    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    # Otherwise, run the coroutine in the current thread:
    return loop.run_until_complete(coro)
