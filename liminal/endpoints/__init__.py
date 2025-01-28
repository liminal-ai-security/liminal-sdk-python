"""Define endpoints on the client object."""

from __future__ import annotations

import asyncio
from typing import Any, ParamSpec

from liminal.helpers import run_sync
from liminal.helpers.typing import ValidatedResponseT

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

        # If we're not dealing with a coroutine, return the attribute as is:
        if not asyncio.iscoroutinefunction(attr):
            return attr

        def sync_wrapper(
            self: type[SDKEndpoint],  # noqa: ARG001
            method: str,  # noqa: ARG001
            endpoint: str,  # noqa: ARG001
            expected_response_type: type[ValidatedResponseT],  # noqa: ARG001
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> ValidatedResponseT:
            """Define a synchronous wrapper for the detected coroutine.

            Args:
            ----
                self: The endpoint object.
                method: The HTTP method.
                endpoint: The endpoint.
                expected_response_type: The expected response type.
                args: The positional arguments.
                kwargs: The keyword arguments.

            Returns:
            -------
                The result of the coroutine.

            """
            return run_sync(attr(*args, **kwargs))

        # Otherwise, return a synchronous wrapper of the coroutine:
        return sync_wrapper
