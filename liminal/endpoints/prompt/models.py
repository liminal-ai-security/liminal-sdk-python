"""Define models for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options

from liminal.endpoints.thread.models import DeidentifiedToken
from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class AnalysisFinding(BaseModel):
    """Define the schema for an analysis finding.

    This object stores information about a piece of text from a prompt, what sensitive
    data type was detected, and what the current policy is for this type of data.
    """

    start: int
    end: int
    origin: str
    score: float
    score_category: str = field(metadata=field_options(alias="scoreCategory"))
    text: str
    type: str
    policy_action: str = field(metadata=field_options(alias="policyAction"))


@dataclass(frozen=True, kw_only=True)
class AnalyzeResponse(BaseModel):
    """Define the response schema for an analysis request."""

    findings: list[AnalysisFinding]


@dataclass(frozen=True, kw_only=True)
class CleansedToken(BaseModel):
    """Define the schema for a cleansed token."""

    start: int
    end: int
    entity_type: str


@dataclass(frozen=True, kw_only=True)
class HydratedToken(BaseModel):
    """Define the schema for a hydrated token."""

    end: int
    entity_type: str
    start: int


@dataclass(frozen=True, kw_only=True)
class CleanseResponse(BaseModel):
    """Define the response schema for a cleanse request."""

    items: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with cleansed tokens:
    text: str
    items_hashed: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with hashed tokens (which
    # are help in mapping):
    text_hashed: str


@dataclass(frozen=True, kw_only=True)
class HydrateResponse(BaseModel):
    """Define the response schema for a hydrate request."""

    items: list[HydratedToken]
    text: str


@dataclass(frozen=True, kw_only=True)
class ReidentifiedToken(BaseModel):
    """Define the schema for a reidentified token."""

    start: int
    end: int
    entity_type: str
    text: str


@dataclass(frozen=True, kw_only=True)
class ProcessResponse(BaseModel):
    """Define the response schema for a process request."""

    thread_id: int = field(metadata=field_options(alias="threadId"))
    chat_id: int = field(metadata=field_options(alias="chatId"))
    input_text: str = field(metadata=field_options(alias="inputText"))
    deidentified_input_text_data: CleanseResponse = field(
        metadata=field_options(alias="deidentifiedInputTextData")
    )
    deidentified_context_history: list[DeidentifiedToken] = field(
        metadata=field_options(alias="deidentifiedContextHistory")
    )
    llm_model: str = field(metadata=field_options(alias="llmModel"))
    raw_llm_response_text: str = field(
        metadata=field_options(alias="rawLLMResponseText")
    )
    reidentified_llm_response_text: str = field(
        metadata=field_options(alias="reidentifiedLLMResponseText")
    )
    reidentified_llm_response_items: list[ReidentifiedToken] = field(
        metadata=field_options(alias="reidentifiedLLMResponseItems")
    )
