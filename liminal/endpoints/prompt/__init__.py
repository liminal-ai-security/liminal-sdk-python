"""Define the prompts endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

from liminal.helpers.typing import ValidatedResponseT

from .models import AnalyzeResponse, CleanseResponse


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

    async def analyze(self, thread_id: int, prompt: str) -> AnalyzeResponse:
        """Analyze a prompt for sensitive data.

        Args:
            thread_id: The ID of the thread to analyze the prompt for.
            prompt: The prompt to analyze.

        Returns:
            An object that contains identified sensitive data.
        """
        return cast(
            AnalyzeResponse,
            await self._request_and_validate(
                "POST",
                "/sdk/analyze_response",
                AnalyzeResponse,
                json={"threadId": thread_id, "text": prompt},
            ),
        )

    async def cleanse(self, thread_id: int, prompt: str) -> CleanseResponse:
        """Cleanse a prompt of sensitive data.

        Args:
            thread_id: The ID of the thread to cleanse the prompt for.
            prompt: The prompt to cleanse.

        Returns:
            An object that contains a cleansed version of the prompt.
        """
        return cast(
            CleanseResponse,
            await self._request_and_validate(
                "POST",
                "/sdk/cleanse_response",
                CleanseResponse,
                json={"threadId": thread_id, "text": prompt},
            ),
        )
