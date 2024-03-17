"""Define the LLM endpoint."""

from collections.abc import Awaitable, Callable
from typing import cast

from liminal.endpoints.llm.models import ModelInstances
from liminal.errors import ModelInstanceUnknownError
from liminal.helpers.typing import ValidatedResponseT


class LLMEndpoint:
    """Define the LLM endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize."""
        self._request_and_validate = request_and_validate

    async def get_available_model_instances(self) -> list[ModelInstances]:
        """Get available model instances."""
        return cast(
            list[ModelInstances],
            await self._request_and_validate(
                "GET", "/api/v1/model-instances", list[ModelInstances]
            ),
        )

    async def get_model_instance(self, model_instance_name: str) -> ModelInstances:
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
            raise ModelInstanceUnknownError(
                f"Unknown model instance name: {model_instance_name}"
            ) from err

        if model_instance.model_connection is None:
            raise ModelInstanceUnknownError(
                f"Unknown model instance name: {model_instance_name}"
            )

        return model_instance
