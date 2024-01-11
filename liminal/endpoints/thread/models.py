"""Define models for the LLM endpoint."""
from __future__ import annotations

from typing import Literal

from liminal.endpoints.llm.models import LLMService
from liminal.helpers.model import BaseModel


class Thread(BaseModel):
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
