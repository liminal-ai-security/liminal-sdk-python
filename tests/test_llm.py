"""Define LLM endpoint tests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.errors import ModelInstanceUnknownError
from tests.common import TEST_API_SERVER_URL


@pytest.mark.asyncio()
async def test_get_available_model_instances(
    httpx_mock: HTTPXMock, mock_client: Client, model_instances_response: dict[str, Any]
) -> None:
    """Test getting available model instances.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        model_instances_response: A model instances response.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances",
        json=model_instances_response,
    )

    instances = await mock_client.llm.get_available_model_instances()
    assert instances[0].id == 1
    assert instances[0].policy_group_id == 1
    assert instances[0].trainer_thread_id is None
    assert instances[0].user_id is None
    assert instances[0].instructions == ""
    assert instances[0].name == "GPT3.5"
    assert instances[0].created_at == datetime(
        2024, 2, 29, 11, 27, 3, 792000, tzinfo=UTC
    )
    assert instances[0].deleted_at is None
    assert instances[0].updated_at == datetime(
        2024, 2, 29, 11, 27, 3, 792000, tzinfo=UTC
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("model_instance_name", "should_exist"),
    [
        ("GPT3.5", True),
        ("GPT3.6", False),
        ("GPT4", False),
    ],
)
async def test_get_model_instance_by_name(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    model_instance_name: str,
    model_instances_response: dict[str, Any],
    should_exist: bool,
) -> None:
    """Test getting a model instance by name.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        model_instance_name: The name of the model instance to retrieve.
        model_instances_response: dict[str, Any],
        should_exist: Whether the model instance should exist.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances",
        json=model_instances_response,
    )

    if should_exist:
        instance = await mock_client.llm.get_model_instance(model_instance_name)
        assert instance.id == 1
        assert instance.policy_group_id == 1
        assert instance.name == "GPT3.5"
        assert instance.created_at == datetime(
            2024, 2, 29, 11, 27, 3, 792000, tzinfo=UTC
        )
        assert instance.deleted_at is None
        assert instance.updated_at == datetime(
            2024, 2, 29, 11, 27, 3, 792000, tzinfo=UTC
        )
    else:
        with pytest.raises(
            ModelInstanceUnknownError, match="Unknown model instance name"
        ):
            await mock_client.llm.get_model_instance(model_instance_name)
