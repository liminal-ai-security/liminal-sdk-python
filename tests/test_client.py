"""Define client tests."""

from __future__ import annotations

import json
from typing import NamedTuple

import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import RequestError
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID


@pytest.mark.asyncio
async def test_bad_endpoint(httpx_mock: HTTPXMock, mock_client: Client) -> None:
    """Test for a bad endpoint.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/foobar",
        content=b"Not Found",
        status_code=404,
    )

    with pytest.raises(RequestError, match="Not Found"):
        await mock_client._request("GET", "/foobar")


@pytest.mark.asyncio
async def test_bad_endpoint_generated_client(
    httpx_mock: HTTPXMock, patch_liminal_api_server: None, patch_msal: None
) -> None:
    """Test for a bad endpoint with an internally generated HTTPX AsyncClient.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        patch_liminal_api_server: Ensure the Liminal API server is patched.
        patch_msal: Ensure the MSAL library is patched.

    """
    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    _ = await Client.authenticate_from_auth_provider(
        TEST_API_SERVER_URL, microsoft_auth_provider
    )


class UnexpectedResponseTest(NamedTuple):
    """Define an unexpected response test."""

    content: bytes


@pytest.mark.asyncio
@pytest.mark.parametrize(
    UnexpectedResponseTest._fields,
    [
        UnexpectedResponseTest(content=b"This is unexpected"),
        UnexpectedResponseTest(content=json.dumps({"foo": "bar"}).encode()),
    ],
)
async def test_unexpected_response(
    content: bytes, httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test for a bad endpoint.

    Args:
    ----
        content: The content to return in the response.
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances",
        content=content,
    )

    with pytest.raises(RequestError, match="Could not validate response"):
        _ = await mock_client.llm.get_available_model_instances()
