"""Define the prompts endpoint."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
import json
from typing import Any, cast

from mashumaro.codecs.json import json_decode

from liminal.const import LOGGER, SOURCE
from liminal.endpoints.prompt.models import (
    AnalysisFindings,
    CleanseData,
    HydrateData,
    StreamResponseChunk,
    SubmitData,
)
from liminal.endpoints.prompt.schemas import (
    AnalyzeResponse,
    CleanseResponse,
    HydrateResponse,
    SubmitResponse,
)
from liminal.helpers.typing import ValidatedResponseT


class PromptEndpoint:
    """Define the prompts endpoint."""

    def __init__(
        self,
        request_and_validate: Callable[..., Awaitable[ValidatedResponseT]],
        stream: Callable[..., AsyncIterator[str]],
    ) -> None:
        """Initialize.

        Args:
        ----
            request_and_validate: The request and validate function.
            stream: The stream function.

        """
        self._request_and_validate = request_and_validate
        self._stream = stream

    def _generate_payload_for_request(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalysisFindings | None = None,
    ) -> dict[str, Any]:
        """Generate a payload for the request.

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
            A request payload.

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

        return payload

    async def analyze(self, model_instance_id: int, prompt: str) -> AnalysisFindings:
        """Analyze a prompt for sensitive data.

        Args:
        ----
            model_instance_id: The ID of the model instance to analyze the prompt with.
            prompt: The prompt to analyze.

        Returns:
        -------
            An object that contains identified sensitive data ("findings").

        """
        response = cast(
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
        return response.data

    async def cleanse(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalysisFindings | None = None,
    ) -> CleanseData:
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
        payload = self._generate_payload_for_request(
            model_instance_id, prompt, thread_id=thread_id, findings=findings
        )
        response = cast(
            CleanseResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/cleanse",
                CleanseResponse,
                json=payload,
            ),
        )
        return response.data

    async def hydrate(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
    ) -> HydrateData:
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
        response = cast(
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
        return response.data

    async def stream(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalysisFindings | None = None,
    ) -> AsyncIterator[StreamResponseChunk]:
        """Submit a prompt to a thread and stream a response from the LLM.

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
        payload = self._generate_payload_for_request(
            model_instance_id, prompt, thread_id=thread_id, findings=findings
        )
        payload["isStreaming"] = True
        async for chunk in self._stream("POST", "/api/v1/prompts/submit", json=payload):
            try:
                yield json_decode(chunk, StreamResponseChunk)
            except json.decoder.JSONDecodeError:
                LOGGER.warning("Stream returned incomplete JSON chunk: %s", chunk)
                yield StreamResponseChunk(content=chunk, finish_reason=None)

    async def submit(
        self,
        model_instance_id: int,
        prompt: str,
        *,
        thread_id: int | None = None,
        findings: AnalysisFindings | None = None,
    ) -> SubmitData:
        """Submit a prompt to a thread and get a complete response from the LLM.

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
        payload = self._generate_payload_for_request(
            model_instance_id, prompt, thread_id=thread_id, findings=findings
        )
        response = cast(
            SubmitResponse,
            await self._request_and_validate(
                "POST",
                "/api/v1/prompts/submit",
                SubmitResponse,
                json=payload,
            ),
        )
        return response.data
