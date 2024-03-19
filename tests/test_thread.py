"""Define thread endpoint tests."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from tests.common import TEST_API_SERVER_URL


@pytest.mark.asyncio()
async def test_create(
    httpx_mock: HTTPXMock, mock_client: Client, threads_create_response: dict[str, Any]
) -> None:
    """Test the create thread method.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        threads_create_response: The response from the endpoint.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/threads?source=sdk",
        json=threads_create_response,
    )

    thread = await mock_client.thread.create(123, "My thread")
    assert thread.id == 167
    assert thread.model_instance_id == 5
    assert thread.user_id == 2
    assert thread.name == "My thread"
    assert thread.source == "sdk"
    assert thread.created_at == "2024-03-18T23:22:17.976Z"
    assert thread.deleted_at is None
    assert thread.updated_at == "2024-03-18T23:22:17.976Z"  # type: ignore[unreachable]
    assert thread.chats == []


@pytest.mark.asyncio()
async def test_get_available(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    threads_get_available_response: dict[str, Any],
) -> None:
    """Test the get available threads method.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        threads_get_available_response: The response from the endpoint.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/threads?source=sdk",
        json=threads_get_available_response,
    )

    threads = await mock_client.thread.get_available()
    assert len(threads) == 1


@pytest.mark.asyncio()
async def test_get_by_id(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    threads_get_by_id_response: dict[str, Any],
) -> None:
    """Test the get available threads method.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        threads_get_by_id_response: The response from the endpoint.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/threads/161?source=sdk",
        json=threads_get_by_id_response,
    )

    thread = await mock_client.thread.get_by_id(161)
    assert thread.name == "My thread"


@pytest.mark.asyncio()
async def test_get_deidentified_context_history(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    threads_get_deidentified_context_history_response: dict[str, Any],
) -> None:
    """Test the get available threads method.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        threads_get_deidentified_context_history_response: The response from the endpoint.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/get_context_history?source=sdk",
        json=threads_get_deidentified_context_history_response,
    )

    tokens = await mock_client.thread.get_deidentified_context_history(161)
    assert len(tokens) == 9
