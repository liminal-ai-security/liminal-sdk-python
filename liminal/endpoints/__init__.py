"""Define endpoints on the client object."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, ParamSpec

from liminal.helpers import run_sync

_P = ParamSpec("_P")


class SDKEndpoint:  # pylint: disable=too-few-public-methods
    """Define a common base for all endpoint objects."""


class SyncEndpointWrapper:  # pylint: disable=too-few-public-methods
    """Define a synchronous wrapper for an endpoint object."""

    def __init__(self, endpoint: SDKEndpoint) -> None:
        """Initialize.

        Args:
        ----
            endpoint: The endpoint to wrap.

        """
        self._endpoint = endpoint

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Get an attribute from the wrapped endpoint.

        Args:
        ----
            name: The name of the attribute to get.

        Returns:
        -------
            The attribute.

        """
        attr = getattr(self._endpoint, name)

        if asyncio.iscoroutinefunction(attr):
            return self._wrap_coroutinefunction(attr)
        if isinstance(attr, Callable):
            return self._wrap_async_generator(attr)
        return attr

    def _wrap_async_generator(
        self, async_gen: AsyncIterator
    ) -> Callable[[], Iterator]:
        """Return a synchronous wrapper for the given async generator.

        Args:
        ----
            async_gen: The async generator to wrap.

        Returns:
        -------
            The synchronous wrapper.

        """

        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Iterator:
            """Define the synchronous wrapper.

            Args:
            ----
                args: The positional arguments.
                kwargs: The keyword arguments.

            Returns:
            -------
                The synchronous generator.

            """
            while True:
                try:
                    yield run_sync(anext(async_gen))
                except StopAsyncIteration:
                    break

        return wrapper

    def _wrap_coroutinefunction(
        self, coro_func: Callable[..., Awaitable]
    ) -> Callable[_P, Any]:
        """Return a synchronous wrapper for the given coroutine.

        Args:
        ----
            coro_func: The coroutine to wrap.

        Returns:
        -------
            The synchronous wrapper.

        """

        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Any:  # noqa: ANN401
            """Define the synchronous wrapper.

            Args:
            ----
                args: The positional arguments.
                kwargs: The keyword arguments.

            Returns:
            -------
                The result of the coroutine.

            """
            coro_result = coro_func(*args, **kwargs)
            if isinstance(coro_result, AsyncIterator):
                return self._wrap_async_generator(coro_result)
            return run_sync(coro_result)

        return wrapper
