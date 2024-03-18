"""Define Liminal auth tests tests."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import logging
from time import time
from unittest.mock import Mock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID

TEST_REFRESH_TOKEN = "REDACTED"  # noqa: S105


@pytest.mark.asyncio()
async def test_auth_via_refresh_token_existing_client(
    httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test authenticating via a refresh token with an existing client.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/refresh-token?source=sdk",
        headers=[
            ("Set-Cookie", "accessToken=NEW_TOKEN"),
            ("Set-Cookie", f"accessTokenExpiresAt={(int(time()) + 3600) * 1000}"),
            ("Set-Cookie", "refreshToken=NEW_TOKEN"),
        ],
    )

    old_access_token = mock_client._access_token
    old_refresh_token = mock_client._refresh_token

    await mock_client.authenticate_from_refresh_token()

    assert mock_client._access_token != old_access_token
    assert mock_client._refresh_token != old_refresh_token


@pytest.mark.asyncio()
async def test_auth_via_refresh_token_new_client(
    httpx_mock: HTTPXMock, patch_msal: None
) -> None:
    """Test authenticating via a refresh token with a new client.

    Args:
        httpx_mock: The HTTPX mock fixture.
        patch_msal: Ensure the MSAL library is patched.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/refresh-token?source=sdk",
        headers=[
            ("Set-Cookie", "accessToken=NEW_TOKEN"),
            ("Set-Cookie", f"accessTokenExpiresAt={(int(time()) + 3600) * 1000}"),
            ("Set-Cookie", "refreshToken=NEW_TOKEN"),
        ],
    )

    microsoft_auth_provider = MicrosoftAuthProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )
        await client.authenticate_from_refresh_token(refresh_token=TEST_REFRESH_TOKEN)
        assert client._access_token is not None
        assert client._access_token_expires_at is not None
        assert client._refresh_token is not None


@pytest.mark.asyncio()
async def test_expired_access_token(
    caplog: Mock, httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test handling an expired access token.

    Args:
        caplog: A mocked logging utility.
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    caplog.set_level(logging.DEBUG)

    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/refresh-token?source=sdk",
        headers=[
            ("Set-Cookie", "accessToken=NEW_TOKEN"),
            ("Set-Cookie", f"accessTokenExpiresAt={(int(time()) + 3600) * 1000}"),
            ("Set-Cookie", "refreshToken=NEW_TOKEN"),
        ],
    )

    old_access_token = mock_client._access_token
    old_refresh_token = mock_client._refresh_token

    # Simulate an access token expiration timestamp in the past:
    mock_client._access_token_expires_at = datetime.fromtimestamp(
        int(time()) - 1, tz=UTC
    )

    findings = await mock_client.prompt.analyze(1, "This is a test prompt")

    # Assert the we actually refreshed the tokens:
    assert mock_client._access_token != old_access_token
    assert mock_client._refresh_token != old_refresh_token
    assert any(m for m in caplog.messages if "Access token expired, refreshing..." in m)

    # Assert that the original call produced results:
    assert len(findings.findings) == 5


@pytest.mark.asyncio()
async def test_expired_access_token_concurrent_calls(
    caplog: Mock, httpx_mock: HTTPXMock, mock_client: Client
) -> None:
    """Test handling an expired access token with concurrent incoming calls.

    Args:
        caplog: A mocked logging utility.
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.

    """
    caplog.set_level(logging.DEBUG)

    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/refresh-token?source=sdk",
        headers=[
            ("Set-Cookie", "accessToken=NEW_TOKEN"),
            ("Set-Cookie", f"accessTokenExpiresAt={(int(time()) + 3600) * 1000}"),
            ("Set-Cookie", "refreshToken=NEW_TOKEN"),
        ],
    )

    old_access_token = mock_client._access_token
    old_refresh_token = mock_client._refresh_token

    # Simulate an access token expiration timestamp in the past:
    mock_client._access_token_expires_at = datetime.fromtimestamp(
        int(time()) - 1, tz=UTC
    )

    tasks = [
        mock_client.llm.get_available_model_instances(),
        mock_client.prompt.analyze(1, "This is a test prompt"),
    ]
    results = await asyncio.gather(*tasks)

    # Assert the we actually refreshed the tokens:
    assert mock_client._access_token != old_access_token
    assert mock_client._refresh_token != old_refresh_token
    assert any(m for m in caplog.messages if "Access token expired, refreshing..." in m)

    # Assert that the original call produced results:
    assert len(results) == 2
