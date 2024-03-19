"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from mashumaro import field_options

from liminal.endpoints.llm.models import ModelInstance
from liminal.helpers.model import BaseResponseModel


@dataclass(frozen=True, kw_only=True)
class DeidentifiedToken(BaseResponseModel):
    """Define the schema for a deidentified token."""

    deid_text: str = field(metadata=field_options(alias="deidText"))
    hash_text: str = field(metadata=field_options(alias="hashText"))


@dataclass(frozen=True, kw_only=True)
class Chat(BaseResponseModel):
    """Define the schema for a chat."""

    id: int
    thread_id: int = field(metadata=field_options(alias="threadId"))
    deidentified_input: str = field(metadata=field_options(alias="deidentifiedInput"))
    dedentified_text: list[DeidentifiedToken] = field(
        metadata=field_options(alias="deidentifiedText")
    )
    hashed_deidentified_input: str = field(
        metadata=field_options(alias="hashedDeidentifiedInput")
    )
    input: str
    llm_output: str = field(metadata=field_options(alias="llmOutput"))
    output: str
    status: str
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime | None = field(
        default=None, metadata=field_options(alias="updatedAt")
    )
    deleted_at: datetime = field(metadata=field_options(alias="deletedAt"))


@dataclass(frozen=True, kw_only=True)
class Thread(BaseResponseModel):
    """Define the schema for a thread."""

    id: int
    user_id: int = field(metadata=field_options(alias="userId"))
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))
    name: str
    source: Literal["sdk"]
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    deleted_at: datetime | None = field(
        default=None, metadata=field_options(alias="deletedAt")
    )
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
    model_instance: ModelInstance = field(metadata=field_options(alias="modelInstance"))
