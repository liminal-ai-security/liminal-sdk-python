"""Define models for the LLM endpoint."""

from __future__ import annotations

import msgspec

from liminal.endpoints.thread.models import DeidentifiedToken
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
    score_category: str = msgspec.field(name="scoreCategory")
    text: str
    type: str
    policy_action: str = msgspec.field(name="policyAction")


class AnalyzeResponse(BaseModel):
    """Define the response schema for an analysis request."""

    findings: list[AnalysisFinding]


class CleansedToken(BaseModel):
    """Define the schema for a cleansed token."""

    start: int
    end: int
    entity_type: str


class HydratedToken(BaseModel):
    """Define the schema for a hydrated token."""

    end: int
    entity_type: str
    start: int


class CleanseResponse(BaseModel):
    """Define the response schema for a cleanse request."""

    items: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with cleansed tokens:
    text: str
    items_hashed: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with hashed tokens (which
    # are help in mapping):
    text_hashed: str


class HydrateResponse(BaseModel):
    """Define the response schema for a hydrate request."""

    items: list[HydratedToken]
    text: str


class ReidentifiedToken(BaseModel):
    """Define the schema for a reidentified token."""

    start: int
    end: int
    entity_type: str
    text: str


class ProcessResponse(BaseModel):
    """Define the response schema for a process request."""

    thread_id: int = msgspec.field(name="threadId")
    chat_id: int = msgspec.field(name="chatId")
    input_text: str = msgspec.field(name="inputText")
    deidentified_input_text_data: CleanseResponse = msgspec.field(
        name="deidentifiedInputTextData"
    )
    deidentified_context_history: list[DeidentifiedToken] = msgspec.field(
        name="deidentifiedContextHistory"
    )
    llm_model: str = msgspec.field(name="llmModel")
    raw_llm_response_text: str = msgspec.field(name="rawLLMResponseText")
    reidentified_llm_response_text: str = msgspec.field(
        name="reidentifiedLLMResponseText"
    )
    reidentified_llm_response_items: list[ReidentifiedToken] = msgspec.field(
        name="reidentifiedLLMResponseItems"
    )
