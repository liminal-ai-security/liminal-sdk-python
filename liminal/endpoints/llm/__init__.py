"""Define the LLM endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

from liminal.helpers.typing import ValidatedResponseT

from .models import ModelInstances


class LLMEndpoint:
    """Define the LLM endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize."""
        self._request_and_validate = request_and_validate

    async def get_available_model_instances(self) -> list[ModelInstances]:
        """Get available LLMs."""
        return cast(
            list[ModelInstances],
            await self._request_and_validate(
                "GET", "/api/v1/model-instances", list[ModelInstances]
            ),
        )
