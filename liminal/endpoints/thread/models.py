"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal

from mashumaro import field_options

from liminal.endpoints.llm.models import ModelInstance
from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class DeidentifiedToken(BaseModel):
    """Define the schema for a deidentified token."""

    deid_text: str = field(metadata=field_options(alias="deidText"))
    hash_text: str = field(metadata=field_options(alias="hashText"))


@dataclass(frozen=True, kw_only=True)
class Chat(BaseModel):
    """Define the schema for a chat."""

    id: int

    # References:
    thread_id: int = field(metadata=field_options(alias="threadId"))

    # Fields:
    cleansed_input: str = field(metadata=field_options(alias="cleansedInput"))
    hydrated_output: str = field(metadata=field_options(alias="hydratedOutput"))
    raw_input: str = field(metadata=field_options(alias="rawInput"))
    raw_output: str = field(metadata=field_options(alias="rawOutput"))
    status: str

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime | None = field(
        default=None, metadata=field_options(alias="updatedAt")
    )
    deleted_at: datetime = field(metadata=field_options(alias="deletedAt"))


class ThreadType(StrEnum):
    """Define a thread type."""

    # The thread is default:
    DEFAULT = "default"

    # The thread used for training a model instance:
    TRAINER = "trainer"


@dataclass(frozen=True, kw_only=True)
class Thread(BaseModel):
    """Define the schema for a thread."""

    id: int

    # References:
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))
    user_id: int = field(metadata=field_options(alias="userId"))

    # Fields:
    name: str
    source: Literal["sdk"]
    type: ThreadType

    # Relations:
    model_instance: ModelInstance = field(metadata=field_options(alias="modelInstance"))

    # Timestamps:
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
