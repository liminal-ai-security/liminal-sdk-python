"""Define schemas for the LLM endpoint."""

from __future__ import annotations

from dataclasses import dataclass

from liminal.endpoints.llm.models import ModelInstance
from liminal.helpers.schema import BaseResponseSchema


@dataclass(frozen=True, kw_only=True)
class GetAvailableModelInstancesResponse(BaseResponseSchema):
    """Define the response schema for getting all available model instances."""

    data: list[ModelInstance]
