"""Define models for the LLM endpoint."""

from __future__ import annotations

from typing import Literal

from liminal.endpoints.llm.models import LLMService
from liminal.helpers.model import BaseModel


class DeidentifiedToken(BaseModel):
    """Define the schema for a deidentified token."""

    deidText: str
    hashText: str


class Thread(BaseModel):
    """Define the schema for a thread."""

    id: int
    name: str
    userId: str
    llmServiceModelKey: str
    createdAt: str
    updatedAt: str
    source: Literal["sdk"]
    chats: list
    model: LLMService


# def test():
#     return [
#         {
#             "deidText": "PERSON_1",
#             "hashText": "e7jQ5Yi9nRXxNyK6NBW4Q2GNgyHunDgD+mqNACWQzPY=",
#         },
#         {
#             "deidText": "PERSON_0",
#             "hashText": "/orm1sYaK1f6EOMnN2ewyXEznsyulcuUYTOwK2DKC24=",
#         },
#         {
#             "deidText": "LOCATION_0",
#             "hashText": "1MfC83PELHvWN53CfVHVFGCHxCbPzbfmO8Dmdg",
#         },
#         {
#             "deidText": "EMAIL_ADDRESS_0",
#             "hashText": "wbDUkZncjP3Q6GZNTG0DV7NmUdpO8xcGjrlHZF",
#         },
#         {
#             "deidText": "DATE_TIME_0",
#             "hashText": "t/C9jwx6cw9qGezOWCbYg5a5mZI+3reZItYf3gS5P2I=",
#         },
#     ]
