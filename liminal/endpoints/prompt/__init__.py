"""Define the prompts endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

from liminal.helpers.typing import ValidatedResponseT

from .models import AnalyzeResponse


class PromptEndpoint:
    """Define the prompts endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize.

        Args:
            request_and_validate: The request and validate function.
        """
        self._request_and_validate = request_and_validate

    async def analyze(self, prompt: str) -> AnalyzeResponse:
        """Analyze a prompt for sensitive data.

        Args:
            prompt: The prompt to analyze.

        Returns:
            A series of "findings" that denote identified sensitive data in the prompt.
        """
        return cast(
            AnalyzeResponse,
            await self._request_and_validate(
                "POST", "/sdk/analyze_response", AnalyzeResponse, json={"text": prompt}
            ),
        )
