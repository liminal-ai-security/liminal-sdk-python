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
