"""Define the LLM endpoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from liminal.endpoints.llm.models import ModelInstance
from liminal.errors import ModelInstanceUnknownError
from liminal.helpers.typing import ValidatedResponseT


class LLMEndpoint:
    """Define the LLM endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize.

        Args:
            request_and_validate: The function to request and validate a response.

        """
        self._request_and_validate = request_and_validate

    async def get_available_model_instances(self) -> list[ModelInstance]:
        """Get available model instances.

        Returns:
            A list of available model instances.

        """
        return cast(
            list[ModelInstance],
            await self._request_and_validate(
                "GET", "/api/v1/model-instances", list[ModelInstance]
            ),
        )

    async def get_model_instance(self, model_instance_name: str) -> ModelInstance:
        """Get a model instance by name.

        Args:
            model_instance_name: The name of the model instance to retrieve.

        Returns:
            The model instance.

        Raises:
            ModelInstanceUnknownError: When the model instance is unknown.

        """
        model_instances = await self.get_available_model_instances()

        try:
            model_instance = next(
                instance
                for instance in model_instances
                if instance.name == model_instance_name
            )
        except StopIteration as err:
            msg = f"Unknown model instance name: {model_instance_name}"
            raise ModelInstanceUnknownError(msg) from err

        if model_instance.model_connection is None:
            msg = f"Unknown model instance name: {model_instance_name}"
            raise ModelInstanceUnknownError(msg)

        return model_instance
