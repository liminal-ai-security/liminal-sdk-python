"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from mashumaro import field_options

from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class DeidentifiedToken(BaseModel):
    """Define the schema for a deidentified token."""

    deid_text: str = field(metadata=field_options(alias="deidText"))
    hash_text: str = field(metadata=field_options(alias="hashText"))


@dataclass(frozen=True, kw_only=True)
class Thread(BaseModel):
    """Define the schema for a thread."""

    id: int
    name: str
    user_id: int = field(metadata=field_options(alias="userId"))
    model_instance_id: int = field(metadata=field_options(alias="modelInstanceId"))
    created_at: str = field(metadata=field_options(alias="createdAt"))
    updated_at: str = field(metadata=field_options(alias="updatedAt"))
    source: Literal["sdk"]
