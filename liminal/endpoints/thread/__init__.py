"""Define the threads endpoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from liminal.const import SOURCE
from liminal.endpoints.thread.models import Thread
from liminal.endpoints.thread.schemas import (
    CreateThreadResponse,
    GetAvailableThreadsResponse,
    GetThreadByIdResponse,
)
from liminal.helpers.typing import ValidatedResponseT


class ThreadEndpoint:
    """Define the threads endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize.

        Args:
        ----
            request_and_validate: The request and validate function.

        """
        self._request_and_validate = request_and_validate

    async def create(self, model_instance_id: int, name: str) -> Thread:
        """Create a thread.

        Args:
        ----
            model_instance_id: The model instance id.
            name: The name of the thread.

        Returns:
        -------
            A Thread object representing the created thread.

        """
        response = cast(
            CreateThreadResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/threads",
                CreateThreadResponse,
                json={
                    "name": name,
                    "modelInstanceId": model_instance_id,
                    "source": SOURCE,
                },
            ),
        )
        return response.data

    async def get_available(self) -> list[Thread]:
        """Get available threads.

        Returns
        -------
            A list of Thread objects.

        """
        response = cast(
            GetAvailableThreadsResponse,
            await self._request_and_validate(
                "GET",
                "/api/v1/threads",
                GetAvailableThreadsResponse,
                params={"source": SOURCE},
            ),
        )
        return response.data

    async def get_by_id(self, thread_id: int) -> Thread:
        """Get a thread by ID.

        Args:
        ----
            thread_id: The ID of the thread.

        Returns:
        -------
            A Thread object representing the thread.

        """
        response = cast(
            GetThreadByIdResponse,
            await self._request_and_validate(
                "GET",
                f"/api/v1/threads/{thread_id}",
                GetThreadByIdResponse,
            ),
        )
        return response.data
