"""Define models for the LLM endpoint."""
from __future__ import annotations

from typing import Literal

import msgspec

from liminal.endpoints.llm.models import LLMService


class Thread(msgspec.Struct):
    """Define the schema for a thread."""

    id: int
    name: str
    userId: str
    llmServiceModelKey: str
    createdAt: str
    updatedAt: str
    source: Literal["SDK"]
    chats: list
    model: LLMService
