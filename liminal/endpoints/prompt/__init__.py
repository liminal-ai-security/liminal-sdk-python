"""Define the prompts endpoint."""
from collections.abc import Awaitable, Callable
from typing import cast

import msgspec

from liminal.endpoints.thread.models import DeidentifiedToken
from liminal.helpers.typing import ValidatedResponseT

from .models import AnalyzeResponse, CleanseResponse, ProcessResponse


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
            An object that contains identified sensitive data ("findings").
        """
        return cast(
            AnalyzeResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/sdk/analyze_response",
                AnalyzeResponse,
                json={"threadId": thread_id, "text": prompt},
            ),
        )

    async def cleanse(
        self,
        thread_id: int,
        prompt: str,
        *,
        findings: AnalyzeResponse | None = None,
    ) -> CleanseResponse:
        """Cleanse a prompt of sensitive data.

        Args:
            thread_id: The ID of the thread to cleanse the prompt for.
            prompt: The prompt to cleanse.
            findings: The findings from the analyze endpoint. If this is not provided,
                the analyze endpoint will be called automatically.

        Returns:
            An object that contains a cleansed version of the prompt.
        """
        payload = {"threadId": thread_id, "text": prompt}
        if findings:
            payload["findings"] = msgspec.to_builtins(findings.findings)

        return cast(
            CleanseResponse,
            await self._request_and_validate(
                "POST", "/api/v1/sdk/cleanse_response", CleanseResponse, json=payload
            ),
        )

    async def submit(
        self,
        thread_id: int,
        prompt: str,
        *,
        findings: AnalyzeResponse | None = None,
    ) -> ProcessResponse:
        """Submit a prompt to a thread and get a response from the LLM.

        Args:
            thread_id: The ID of the thread to cleanse the prompt for.
            prompt: The prompt to cleanse.
            findings: The findings from the analyze endpoint. If this is not provided,
                the analyze endpoint will be called automatically.

        Returns:
            An object that contains a response from the LLM.
        """
        payload = {"threadId": thread_id, "text": prompt}
        if findings:
            payload["findings"] = msgspec.to_builtins(findings.findings)

        return cast(
            ProcessResponse,
            await self._request_and_validate(
                "POST", "/api/v1/sdk/process", ProcessResponse, json=payload
            ),
        )
