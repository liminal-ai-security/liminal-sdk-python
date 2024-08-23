"""Define Liminal auth tests tests."""

from __future__ import annotations

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from tests.common import (
    TEST_API_SERVER_URL,
    TEST_HTTPX_DEFAULT_TIMEOUT,
    TEST_SESSION_ID,
    TEST_TOKEN,
)


@pytest.mark.asyncio
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

    async with httpx.AsyncClient(timeout=TEST_HTTPX_DEFAULT_TIMEOUT) as httpx_client:
        client = await Client.authenticate_from_session_id(
            TEST_API_SERVER_URL, TEST_SESSION_ID, httpx_client=httpx_client
        )
        assert client.session_id is not None


@pytest.mark.asyncio
async def test_auth_via_token(httpx_mock: HTTPXMock, patch_msal: None) -> None:
    """Test authenticating via a saved session cookie.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        patch_msal: Ensure the MSAL library is patched.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/test-automation/login",
        headers=[
            ("Set-Cookie", f"session={TEST_SESSION_ID}"),
        ],
    )

    async with httpx.AsyncClient(timeout=TEST_HTTPX_DEFAULT_TIMEOUT) as httpx_client:
        client = await Client.authenticate_from_token(
            TEST_API_SERVER_URL, TEST_TOKEN, httpx_client=httpx_client
        )
        assert client.session_id is not None
