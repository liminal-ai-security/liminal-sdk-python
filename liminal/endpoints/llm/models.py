"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import field_options

from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class ModelConnection(BaseModel):
    """Define the model for an LLM model connection."""

    id: int

    # References:
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))

    # Fields:
    credentials: dict[str, str] | None = field(default_factory=dict)
    model: str
    provider_key: str = field(metadata=field_options(alias="providerKey"))

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))


@dataclass(frozen=True, kw_only=True)
class ModelInstance(BaseModel):
    """Define the model for an LLM model instance that Liminal supports."""

    id: int

    # References:
    policy_group_id: int = field(metadata=field_options(alias="policyGroupId"))
    trainer_thread_id: int | None = field(
        default=None, metadata=field_options(alias="trainerThreadId")
    )
    user_id: int | None = field(default=None, metadata=field_options(alias="userId"))

    # Fields:
    instructions: str
    name: str

    # Relations:
    model_connections: list[ModelConnection] = field(
        metadata=field_options(alias="modelConnections")
    )

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
