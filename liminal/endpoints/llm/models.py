"""Define models for the LLM endpoint."""
from __future__ import annotations

from typing import Literal

import msgspec

from liminal.helpers.model import BaseModel


class LLMService(BaseModel):
    """Define the schema for an LLM service that Liminal supports."""

    id: int
    key: str
    name: str
    provider: str
    status: Literal["Available", "NotAvailable"]
    is_configurable: bool = msgspec.field(name="isConfigurable")
    description: str
    is_stream_capable: bool = msgspec.field(name="isStreamCapable")
    params: dict[str, str] | None
    teams_allowed: list[str] | None = msgspec.field(name="teamsAllowed")
    created_at: str = msgspec.field(name="createdAt")
    updated_at: str = msgspec.field(name="updatedAt")
    model_key: str | None = msgspec.field(name="modelKey", default=None)


class LLMInstances(BaseModel):
    """Define the schema for an LLM model instance that Liminal supports."""

    id: int
    policyGroupId: int
    model: str
    name: str
    providerKey: str
    params: dict[str, str] | None
    created_at: str = msgspec.field(name="createdAt")
    updated_at: str = msgspec.field(name="updatedAt")
    apiKey: str | None = msgspec.field(name="apiKey", default=None)
    maskedApiKey: str | None = msgspec.field(name="maskedApiKey", default=None)
