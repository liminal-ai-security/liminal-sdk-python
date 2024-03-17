"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options

from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class ModelConnection(BaseModel):
    """Define the schema for an LLM model connection."""

    id: int
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))
    model: str
    provider_key: str = field(metadata=field_options(alias="providerKey"))
    params: dict[str, str] | None
    created_at: str = field(metadata=field_options(alias="createdAt"))
    updated_at: str = field(metadata=field_options(alias="updatedAt"))
    api_key: str | None = field(default=None, metadata=field_options(alias="apiKey"))
    masked_api_key: str | None = field(
        default=None, metadata=field_options(alias="maskedApiKey")
    )
    deleted_at: str | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )


@dataclass(frozen=True, kw_only=True)
class ModelInstance(BaseModel):
    """Define the schema for an LLM model instance that Liminal supports."""

    id: int
    policy_group_id: int = field(metadata=field_options(alias="policyGroupId"))
    model_connection: ModelConnection | None = field(
        metadata=field_options(alias="modelConnection")
    )
    name: str
    created_at: str = field(metadata=field_options(alias="createdAt"))
    updated_at: str = field(metadata=field_options(alias="updatedAt"))
    deleted_at: str | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
