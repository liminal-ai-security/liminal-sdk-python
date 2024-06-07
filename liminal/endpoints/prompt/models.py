"""Define models for the prompt endpoint."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options

from liminal.endpoints.thread.models import DeidentifiedToken
from liminal.helpers.model import BaseModel


@dataclass(frozen=True, kw_only=True)
class AnalysisFinding(BaseModel):
    """Define a detection analysis finding.

    This object stores information about a piece of text from a prompt, what sensitive
    data type was detected, and what the current policy is for this type of data.
    """

    start: int
    end: int
    score: float
    score_category: str = field(metadata=field_options(alias="scoreCategory"))
    text: str
    type: str
    policy_action: str = field(metadata=field_options(alias="policyAction"))


@dataclass(frozen=True, kw_only=True)
class AnalysisFindings(BaseModel):
    """Define consolidated detection analysis findings."""

    findings: list[AnalysisFinding]


@dataclass(frozen=True, kw_only=True)
class CleanseData(BaseModel):
    """Define the result of a cleanse request."""

    items: list[CleansedToken]
    # Represents the prompt with the sensitive data replaced with cleansed tokens:
    text: str
    items_hashed: list[CleansedToken] = field(
        metadata=field_options(alias="itemsHashed")
    )
    # Represents the prompt with the sensitive data replaced with hashed tokens (which
    # are help in mapping):
    text_hashed: str = field(metadata=field_options(alias="textHashed"))


@dataclass(frozen=True, kw_only=True)
class CleansedToken(BaseModel):
    """Define a cleansed token."""

    start: int
    end: int
    entity_type: str = field(metadata=field_options(alias="entityType"))


@dataclass(frozen=True, kw_only=True)
class HydrateData(BaseModel):
    """Define the result of a hydration request."""

    items: list[HydratedToken]
    text: str


@dataclass(frozen=True, kw_only=True)
class HydratedToken(BaseModel):
    """Define a hydrated token."""

    end: int
    entity_type: str = field(metadata=field_options(alias="entityType"))
    start: int


@dataclass(frozen=True, kw_only=True)
class ReidentifiedToken(BaseModel):
    """Define a reidentified token."""

    start: int
    end: int
    entity_type: str = field(metadata=field_options(alias="entityType"))


@dataclass(frozen=True, kw_only=True)
class StreamResponseChunk(BaseModel):
    """Define a streaming response chunk."""

    content: str
    finish_reason: str | None = field(metadata=field_options(alias="finishReason"))


@dataclass(frozen=True, kw_only=True)
class SubmitData(BaseModel):
    """Define the result of a submit request."""

    thread_id: int = field(metadata=field_options(alias="threadId"))
    chat_id: int = field(metadata=field_options(alias="chatId"))
    input_text: str = field(metadata=field_options(alias="inputText"))
    deidentified_input_text_data: CleanseData = field(
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
