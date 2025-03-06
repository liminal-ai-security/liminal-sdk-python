"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mashumaro import field_options

from liminal.helpers.model import BaseModel


# Define enums to use as types:
class ModelProviderKey(str, Enum):
    """Define the enum for the model provider key."""

    ANTHROPIC = "anthropic"
    AWS_BEDROCK = "aws_bedrock"
    AWS_SAGEMAKER = "aws_sagemaker"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    COPILOT_STUDIO = "copilot_studio"
    DEEPSEEK = "deepseek"
    GOOGLE_AI_STUDIO = "google_ai_studio"
    GOOGLE_VERTEX_AI = "google_vertex_ai"
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    XAI = "xai"


@dataclass(frozen=True, kw_only=True)
class ModelConnection(BaseModel):
    """Define the model for an LLM model connection."""

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
