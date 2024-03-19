"""Define LLM endpoint tests."""

from __future__ import annotations

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
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        model_instances_response: A model instances response.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances?source=sdk",
        json=model_instances_response,
    )

    instances = await mock_client.llm.get_available_model_instances()
    assert instances[0].id == 1
    assert instances[0].policy_group_id == 1
    assert instances[0].name == "GPT3.5"
    assert instances[0].created_at == "2024-02-29T11:27:03.792Z"
    assert instances[0].deleted_at is None
    assert instances[0].updated_at == "2024-02-29T11:27:03.792Z"
    assert instances[0].teams == []
    assert instances[0].model_connection is not None
    assert instances[0].model_connection.id == 1
    assert instances[0].model_connection.model_instance_id == 1
    assert instances[0].model_connection.model == "gpt-3.5-turbo"
    assert instances[0].model_connection.params == {}
    assert instances[0].model_connection.provider_key == "openai"
    assert instances[0].model_connection.created_at == "2024-02-29T11:27:03.792Z"
    assert instances[0].model_connection.deleted_at is None
    assert instances[0].model_connection.updated_at == "2024-02-29T11:27:03.792Z"
    assert instances[0].model_connection.api_key == ""
    assert instances[0].model_connection.masked_api_key == ""


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
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        model_instance_name: The name of the model instance to retrieve.
        model_instances_response: dict[str, Any],
        should_exist: Whether the model instance should exist.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances?source=sdk",
        json=model_instances_response,
    )

    if should_exist:
        instance = await mock_client.llm.get_model_instance(model_instance_name)
        assert instance.id == 1
        assert instance.policy_group_id == 1
        assert instance.name == "GPT3.5"
        assert instance.created_at == "2024-02-29T11:27:03.792Z"
        assert instance.deleted_at is None
        assert instance.updated_at == "2024-02-29T11:27:03.792Z"
        assert instance.teams == []
        assert instance.model_connection is not None
        assert instance.model_connection.id == 1
        assert instance.model_connection.model_instance_id == 1
        assert instance.model_connection.model == "gpt-3.5-turbo"
        assert instance.model_connection.params == {}
        assert instance.model_connection.provider_key == "openai"
        assert instance.model_connection.created_at == "2024-02-29T11:27:03.792Z"
        assert instance.model_connection.deleted_at is None
        assert instance.model_connection.updated_at == "2024-02-29T11:27:03.792Z"
        assert instance.model_connection.api_key == ""
        assert instance.model_connection.masked_api_key == ""
    else:
        with pytest.raises(
            ModelInstanceUnknownError, match="Unknown model instance name"
        ):
            await mock_client.llm.get_model_instance(model_instance_name)
