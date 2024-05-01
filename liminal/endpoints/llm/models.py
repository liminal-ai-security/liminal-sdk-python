"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mashumaro import field_options

from liminal.helpers.model import BaseResponseModel


# Define enums to use as types:
class ModelProviderKey(str, Enum):
    """Define the enum for the model provider key."""

    ANTHROPIC = "anthropic"
    AWS_BEDROCK = "aws_bedrock"
    AWS_SAGEMAKER = "aws_sagemaker"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass(frozen=True, kw_only=True)
class ModelConnection(BaseResponseModel):
    """Define the schema for an LLM model connection."""

    id: int

    # References:
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))

    # Fields:
    credentials: dict[str, str] | None = field(default_factory=dict)
    model: str
    provider_key: ModelProviderKey = field(metadata=field_options(alias="providerKey"))

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))


@dataclass(frozen=True, kw_only=True)
class ModelInstance(BaseResponseModel):
    """Define the schema for an LLM model instance that Liminal supports."""

    id: int

    # References:
    policy_group_id: int = field(metadata=field_options(alias="policyGroupId"))

    # Fields:
    name: str

    # Relations:
    model_connection: ModelConnection | None = field(
        default=None, metadata=field_options(alias="modelConnection")
    )

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
