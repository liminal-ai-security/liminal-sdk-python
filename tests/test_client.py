"""Define client tests."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import RequestError
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID


@pytest.mark.asyncio()
async def test_bad_endpoint(
    httpx_mock: HTTPXMock,
    msal_cache_token_response: dict[str, Any],
    msal_token_by_device_flow_response: dict[str, Any],
    patch_liminal_api_server: None,
    patch_msal: None,
) -> None:
    """Test for a bad endpoint.

    Args:
        httpx_mock: The HTTPX mock fixture.
        msal_cache_token_response: The MSAL cache token response.
        msal_token_by_device_flow_response: The MSAL token by device flow response.
        patch_liminal_api_server: Ensure the Liminal API server is patched.
        patch_msal: Ensure the MSAL library is patched.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/foobar?source=sdk",
        content=b"Not Found",
        status_code=404,
    )

    microsoft_auth_provider = MicrosoftAuthProvider(TEST_TENANT_ID, TEST_CLIENT_ID)

    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )
        await client.authenticate_from_auth_provider()

        with pytest.raises(RequestError, match="Not Found"):
            await client._request("GET", "/foobar")  # noqa: SLF001
