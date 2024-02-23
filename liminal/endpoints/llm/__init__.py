"""Define the LLM endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

from liminal.helpers.typing import ValidatedResponseT

from .models import LLMInstances, LLMService


class LLMEndpoint:
    """Define the LLM endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize."""
        self._request_and_validate = request_and_validate

    async def get_available(self) -> list[LLMService]:
        """Get available LLMs."""
        return cast(
            list[LLMService],
            await self._request_and_validate("GET", "/v1/models", list[LLMService]),
        )

    async def get_available_model_instances(self) -> list[LLMInstances]:
        """Get available LLMs."""
        return cast(
            list[LLMInstances],
            await self._request_and_validate(
                "GET", "/v1/model-instances", list[LLMInstances]
            ),
        )
