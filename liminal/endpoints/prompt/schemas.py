"""Define schemas for the prompt endpoint."""

from __future__ import annotations

from dataclasses import dataclass

from liminal.endpoints.prompt.models import (
    AnalysisFindings,
    CleanseData,
    HydrateData,
    SubmitData,
)
from liminal.helpers.schema import BaseResponseSchema


@dataclass(frozen=True, kw_only=True)
class AnalyzeResponse(BaseResponseSchema):
    """Define the response schema for an analysis request."""

    data: AnalysisFindings


@dataclass(frozen=True, kw_only=True)
class CleanseResponse(BaseResponseSchema):
    """Define the response schema for a cleanse request."""

    data: CleanseData


@dataclass(frozen=True, kw_only=True)
class HydrateResponse(BaseResponseSchema):
    """Define the response schema for a hydrate request."""

    data: HydrateData


@dataclass(frozen=True, kw_only=True)
class SubmitResponse(BaseResponseSchema):
    """Define the response schema for a submit request."""

    data: SubmitData
