"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass

from liminal.endpoints.thread.models import Thread
from liminal.helpers.schema import BaseResponseSchema


@dataclass(frozen=True, kw_only=True)
class CreateThreadResponse(BaseResponseSchema):
    """Define the schema for a thread creation request."""

    data: Thread


@dataclass(frozen=True, kw_only=True)
class GetAvailableThreadsResponse(BaseResponseSchema):
    """Define the schema for a getting all available threads."""

    data: list[Thread]


@dataclass(frozen=True, kw_only=True)
class GetThreadByIdResponse(BaseResponseSchema):
    """Define the schema for a getting a thread by ID."""

    data: Thread
