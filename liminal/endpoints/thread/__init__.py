"""Define the threads endpoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from httpx import Response

from liminal.endpoints.thread.models import DeidentifiedToken, Thread
from liminal.helpers.typing import ValidatedResponseT


class ThreadEndpoint:
    """Define the threads endpoint."""

    def __init__(
        self,
        request: Callable[..., Awaitable[Response]],
        request_and_validate: Callable[..., Awaitable[ValidatedResponseT]],
    ) -> None:
        """Initialize.

        Args:
            request: The request function.
            request_and_validate: The request and validate function.

        """
        self._request = request
        self._request_and_validate = request_and_validate

    async def create(self, model_instance_id: int, name: str) -> Thread:
        """Create a thread.

        Args:
            model_instance_id: The model instance id.
            name: The name of the thread.

        Returns:
            A Thread object representing the creatd thread.

        """
        return cast(
            Thread,
            await self._request_and_validate(
                "POST",
                "/api/v1/threads",
                Thread,
                json={
                    "name": name,
                    "modelInstanceId": model_instance_id,
                },
            ),
        )

    async def get_available(self) -> list[Thread]:
        """Get available threads.

        Returns:
            A list of Thread objects.

        """
        return cast(
            list[Thread],
            await self._request_and_validate("GET", "/api/v1/threads", list[Thread]),
        )

    async def get_by_id(self, thread_id: int) -> Thread:
        """Get a thread by ID.

        Args:
            thread_id: The ID of the thread.

        Returns:
            A Thread object representing the thread.

        """
        return cast(
            Thread,
            await self._request_and_validate(
                "GET", f"/api/v1/threads/{thread_id}", Thread
            ),
        )

    async def get_deidentified_context_history(
        self, thread_id: int
    ) -> list[DeidentifiedToken]:
        """Get the deidentified context history for a thread.

        Args:
            thread_id: The ID of the thread.

        Returns:
            A list of DeidentifiedToken objects representing the deidentified context
                history.

        """
        return cast(
            list[DeidentifiedToken],
            await self._request_and_validate(
                "POST",
                "/api/v1/sdk/get_context_history",
                list[DeidentifiedToken],
                json={"threadId": thread_id},
            ),
        )
