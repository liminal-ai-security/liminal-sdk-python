"""Define Liminal auth tests tests."""

from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import AuthError
from tests.common import (
    TEST_API_SERVER_URL,
    TEST_CLIENT_ID,
    TEST_SESSION_ID,
    TEST_TENANT_ID,
)


@pytest.mark.asyncio()
async def test_auth_via_session_id(httpx_mock: HTTPXMock, patch_msal: None) -> None:
    """Test authenticating via a saved session cookie.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        patch_msal: Ensure the MSAL library is patched.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/users/me",
        headers=[
            ("Set-Cookie", f"session={TEST_SESSION_ID}"),
        ],
    )

    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )
        await client.authenticate_from_session_id(session_id=TEST_SESSION_ID)
        assert client._session_id is not None


@pytest.mark.asyncio()
async def test_premature_session_id(httpx_mock: HTTPXMock, patch_msal: None) -> None:
    """Test attempting to refresh the access token before actually getting one.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        patch_msal: Ensure the MSAL library is patched.

    """
    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )

        with pytest.raises(AuthError, match="No valid session ID provided"):
            await client.authenticate_from_session_id()


@pytest.mark.asyncio()
async def test_session_id_callback(httpx_mock: HTTPXMock, mock_client: Client) -> None:
    """Test adding and removing a session cookie callback.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        mock_client: Client

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/users/me",
        headers=[
            ("Set-Cookie", f"session={TEST_SESSION_ID}"),
        ],
    )

    # Define and attach a refresh token callback, then refresh the access token:
    session_id_callback = Mock()
    remove_callback = mock_client.add_session_id_callback(session_id_callback)
    await mock_client.authenticate_from_session_id(session_id=TEST_SESSION_ID)

    # Cancel the callback and refresh the access token again:
    remove_callback()
    await mock_client.authenticate_from_session_id()

    # Ensure that the callback was called only once:
    session_id_callback.assert_called_once_with(mock_client._session_id)
