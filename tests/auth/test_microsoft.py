"""Define Microsoft auth tests tests."""

from __future__ import annotations

from unittest.mock import Mock

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import AuthError
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "msal_accounts",
    [
        [],
        [Mock()],
    ],
)
async def test_auth_via_device_code_flow(
    httpx_mock: HTTPXMock,
    patch_liminal_api_server: None,
    patch_msal: None,
) -> None:
    """Test the Microsoft auth provider via the device code flow.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        patch_liminal_api_server: Ensure the Liminal API server is patched.
        patch_msal: Ensure the MSAL library is patched.

    """
    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)

    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )
        await client.authenticate_from_auth_provider()
        assert client._session is not None


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "mock_msal_acquire_token_by_device_flow", [Mock(side_effect=TimeoutError)]
)
async def test_auth_via_device_code_flow_timeout(
    httpx_mock: HTTPXMock,
    mock_msal_acquire_token_by_device_flow: Mock,
    patch_msal: None,
) -> None:
    """Test the Microsoft auth provider via the device code flow.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        mock_msal_acquire_token_by_device_flow: The mocked MSAL acquire_token_by_device
            flow method.
        patch_msal: Ensure the MSAL library is patched.

    """
    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)

    async with httpx.AsyncClient() as httpx_client:
        client = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )

        with pytest.raises(
            AuthError, match="Timed out waiting for authentication challenge"
        ):
            await client.authenticate_from_auth_provider()
