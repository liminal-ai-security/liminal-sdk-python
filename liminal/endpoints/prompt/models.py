"""Define models for the LLM endpoint."""
from __future__ import annotations

import msgspec


class AnalysisFinding(msgspec.Struct):
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


class AnalyzeResponse(msgspec.Struct):
    """Define the response schema for an analysis request."""

    findings: list[AnalysisFinding]


class CleansedToken(msgspec.Struct):
    """Define the schema for a cleansed token."""

    start: int
    end: int
    entity_type: str


class CleanseResponse(msgspec.Struct):
    """Define the response schema for a cleanse request."""

    items: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with cleansed tokens:
    text: str
    items_hashed: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with hashed tokens (which
    # are help in mapping):
    text_hashed: str
