"""Define the prompts endpoint."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from liminal.const import SOURCE
from liminal.endpoints.prompt.models import (
    AnalyzeResponse,
    CleanseResponse,
    HydrateResponse,
    SubmitResponse,
)
from liminal.helpers.typing import ValidatedResponseT


class PromptEndpoint:
    """Define the prompts endpoint."""

    def __init__(
        self, request_and_validate: Callable[..., Awaitable[ValidatedResponseT]]
    ) -> None:
        """Initialize.

        Args:
        ----
            request_and_validate: The request and validate function.

        """
        self._request_and_validate = request_and_validate

    async def analyze(self, model_instance_id: int, prompt: str) -> AnalyzeResponse:
        """Analyze a prompt for sensitive data.

        Args:
        ----
            model_instance_id: The ID of the model instance to analyze the prompt with.
            prompt: The prompt to analyze.

        Returns:
        -------
            An object that contains identified sensitive data ("findings").

        """
        return cast(
            AnalyzeResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/analyze",
                AnalyzeResponse,
                json={
                    "modelInstanceId": model_instance_id,
                    "source": SOURCE,
                    "text": prompt,
                },
            ),
        )

    async def cleanse(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalyzeResponse | None = None,
    ) -> CleanseResponse:
        """Cleanse a prompt of sensitive data.

        Args:
        ----
            model_instance_id: The ID of the model instance to cleanse the prompt with.
            prompt: The prompt to cleanse.
            thread_id: The ID of the thread to cleanse the prompt for. If this is not
                provided, a thread will be created automatically.
            findings: The findings from the analyze endpoint. If this is not provided,
                findings will be created automatically.

        Returns:
        -------
            An object that contains a cleansed version of the prompt.

        """
        payload = {
            "modelInstanceId": model_instance_id,
            "source": SOURCE,
            "text": prompt,
            "threadId": thread_id,
        }
        if findings:
            payload["findings"] = [
                finding.to_dict(by_alias=True) for finding in findings.findings
            ]

        return cast(
            CleanseResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/cleanse",
                CleanseResponse,
                json=payload,
            ),
        )

    async def hydrate(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
    ) -> HydrateResponse:
        """Rehydrate prompt with sensitive data.

        Args:
        ----
            model_instance_id: The ID of the model instance to hydrate the prompt with.
            prompt: The prompt to hydrate.
            thread_id: The ID of the thread to hydrate the prompt for. If this is not
                provided, a thread will be created automatically.

        Returns:
        -------
            An object that contains a rehydrated version of the prompt.

        """
        return cast(
            HydrateResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/hydrate",
                HydrateResponse,
                json={
                    "modelInstanceId": model_instance_id,
                    "source": SOURCE,
                    "text": prompt,
                    "threadId": thread_id,
                },
            ),
        )

    async def submit(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalyzeResponse | None = None,
    ) -> SubmitResponse:
        """Submit a prompt to a thread and get a response from the LLM.

        Args:
        ----
            model_instance_id: The ID of the model instance to submit the prompt with.
            prompt: The prompt to submit.
            thread_id: The ID of the thread to submit the prompt for. If this is not
                provided, a thread will be created automatically.
            findings: The findings from the analyze endpoint. If this is not provided,
                the analyze endpoint will be called automatically.

        Returns:
        -------
            An object that contains a response from the LLM.

        """
        payload = {
            "modelInstanceId": model_instance_id,
            "source": SOURCE,
            "text": prompt,
            "threadId": thread_id,
        }
        if findings:
            payload["findings"] = [
                finding.to_dict(by_alias=True) for finding in findings.findings
            ]

        return cast(
            SubmitResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/submit",
                SubmitResponse,
                json=payload,
            ),
        )
