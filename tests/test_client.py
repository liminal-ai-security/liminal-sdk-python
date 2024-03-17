"""Define client tests."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from tests.common import TEST_API_SERVER_URL, TEST_CLIENT_ID, TEST_TENANT_ID


@pytest.mark.asyncio
async def test_bad_endpoint(httpx_mock: HTTPXMock) -> None:
    """Test for a bad endpoint.

    Args:
        httpx_mock: The HTTPX mock fixture.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/foobar",
        content=b"Not Found",
        status_code=404,
    )

    microsoft_auth_provider = MicrosoftAuthProvider(TEST_TENANT_ID, TEST_CLIENT_ID)

    async with httpx.AsyncClient() as httpx_client:
        _ = Client(
            microsoft_auth_provider, TEST_API_SERVER_URL, httpx_client=httpx_client
        )
