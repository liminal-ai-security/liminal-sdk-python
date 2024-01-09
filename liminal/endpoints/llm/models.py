"""Define models for the LLM endpoint."""
from __future__ import annotations

from typing import Literal

import msgspec


class AvailableLLM(msgspec.Struct):
    """Define the schema for an available LLM."""

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
    model_key: str | None = msgspec.field(name="modelKey")
