"""Define models for the LLM endpoint."""
from __future__ import annotations

import msgspec

from liminal.helpers.model import BaseModel


class ModelInstances(BaseModel):
    """Define the schema for an LLM model instance that Liminal supports."""

    id: int
    policyGroupId: int
    model_connection: ModelConnection | None = msgspec.field(name="modelConnection")
    name: str
    created_at: str = msgspec.field(name="createdAt")
    updated_at: str = msgspec.field(name="updatedAt")


class ModelConnection(BaseModel):
    """Define the schema for an LLM model connection"""

    id: int
    modelInstanceId: int
    model: str
    providerKey: str
    params: dict[str, str] | None
    created_at: str = msgspec.field(name="createdAt")
    updated_at: str = msgspec.field(name="updatedAt")
    apiKey: str | None = msgspec.field(name="apiKey", default=None)
    maskedApiKey: str | None = msgspec.field(name="maskedApiKey", default=None)
    deleted_at: str | None = msgspec.field(name="deletedAt", default=None)
