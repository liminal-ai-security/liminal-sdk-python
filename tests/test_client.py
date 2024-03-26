"""Define client tests."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import RequestError
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID


@pytest.mark.asyncio()
async def test_bad_endpoint(httpx_mock: HTTPXMock, mock_client: Client) -> None:
    """Test for a bad endpoint.

    Args:
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


@pytest.mark.asyncio()
async def test_bad_endpoint_explicit_client(
    access_token_expires_at: int, httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test for a bad endpoint with an explicit HTTPX AsyncClient.

    Args:
        access_token_expires_at: The access token expiration time.
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/login/oauth/access-token",
        headers=[
            ("Set-Cookie", "accessToken=REDACTED"),
            ("Set-Cookie", f"accessTokenExpiresAt={access_token_expires_at}"),
            ("Set-Cookie", "refreshToken=REDACTED"),
        ],
    )

    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/foobar",
        content=b"Not Found",
        status_code=404,
    )

    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    client = Client(microsoft_auth_provider, TEST_API_SERVER_URL)
    await client.authenticate_from_auth_provider()
    with pytest.raises(RequestError, match="Not Found"):
        await mock_client._request("GET", "/foobar")


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "content", [b"This is unexpected", json.dumps({"foo": "bar"}).encode()]
)
async def test_unexpected_response(
    content: bytes, httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test for a bad endpoint.

    Args:
        content: The content to return in the response.
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/model-instances",
        content=b"This is unexpected",
    )

    with pytest.raises(RequestError, match="Could not validate response"):
        _ = await mock_client.llm.get_available_model_instances()
