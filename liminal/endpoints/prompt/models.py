"""Define models for the LLM endpoint."""
from __future__ import annotations

from liminal.helpers.model import BaseModel


class AnalysisFinding(BaseModel):
    """Define the schema for an analysis finding.

    This object stores information about a piece of text from a prompt, what sensitive
    data type was detected, and what the current policy is for this type of data.
    """

    start: int
    end: int
    origin: str
    score: float
    scoreCategory: str
    text: str
    type: str
    policyAction: str


class AnalyzeResponse(BaseModel):
    """Define the response schema for an analysis request."""

    findings: list[AnalysisFinding]


class CleansedToken(BaseModel):
    """Define the schema for a cleansed token."""

    start: int
    end: int
    entity_type: str


class CleanseResponse(BaseModel):
    """Define the response schema for a cleanse request."""

    items: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with cleansed tokens:
    text: str
    items_hashed: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with hashed tokens (which
    # are help in mapping):
    text_hashed: str
