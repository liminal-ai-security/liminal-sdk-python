"""Define the threads endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

from httpx import Response

from liminal.helpers.typing import ValidatedResponseT

from .models import Thread


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

    async def create(self, llm_key: str, name: str) -> Thread:
        """Create a thread.

        Args:
            llm_key: The LLM key.
            name: The name of the thread.

        Returns:
            A Thread object representing the creatd thread.
        """
        return cast(
            Thread,
            await self._request_and_validate(
                "POST",
                "/sdk/thread",
                Thread,
                json={
                    "name": name,
                    "llmServiceModelKey": llm_key,
                },
            ),
        )

    async def get_available(self) -> list[Thread]:
        """Get available threads."""
        return cast(
            list[Thread],
            await self._request_and_validate("GET", "/sdk/thread", list[Thread]),
        )

    async def delete_by_id(self, thread_id: int) -> None:
        """Get a thread by ID."""
        await self._request("DELETE", f"/sdk/thread/{thread_id}")

    async def get_by_id(self, thread_id: int) -> Thread:
        """Get a thread by ID."""
        return cast(
            Thread,
            await self._request_and_validate("GET", f"/sdk/thread/{thread_id}", Thread),
        )
