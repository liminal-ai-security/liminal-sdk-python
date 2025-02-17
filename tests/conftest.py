"""Define dynamic test fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
import json
from typing import Any, cast
from unittest.mock import Mock, patch

import httpx
import pytest
import pytest_asyncio
from pytest_httpx import HTTPXMock, IteratorStream

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.client import DEFAULT_REQUEST_TIMEOUT
from tests.common import (
    TEST_API_SERVER_URL,
    TEST_CLIENT_ID,
    TEST_SESSION_ID,
    TEST_TENANT_ID,
    load_fixture,
)


@pytest.fixture(name="patch_liminal_api_server")
def _patch_liminal_api_server_fixture(httpx_mock: HTTPXMock) -> None:
    """Patch the Liminal API server.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/login/oauth/access-token",
        headers=[
            ("Set-Cookie", f"session={TEST_SESSION_ID}"),
        ],
    )


@pytest.fixture(name="patch_msal")
def _patch_msal_fixture(
    mock_msal_acquire_token_by_device_flow: Mock,
    msal_accounts: list[Mock],
    msal_cache_token_response: dict[str, Any],
    msal_token_by_device_flow_response: dict[str, Any],
) -> Generator[None]:
    """Patch the MSAL library.

    Args:
    ----
        mock_msal_acquire_token_by_device_flow: The MSAL acquire token by device flow
            method.
        msal_accounts: The MSAL accounts.
        msal_cache_token_response: The MSAL cache token response.
        msal_token_by_device_flow_response: The MSAL token by device flow response.

    Yields:
    ------
        None.

    """
    with patch(
        "liminal.auth.microsoft.device_code_flow.PublicClientApplication"
    ) as msal_app:
        msal_app.return_value.get_accounts = Mock(return_value=msal_accounts)
        msal_app.return_value.initiate_device_flow = Mock(
            return_value={
                "message": (
                    "To sign in, use a web browser to open the page "
                    "https://microsoft.com/devicelogin and enter the code ABCD12345 to "
                    "authenticate."
                )
            }
        )
        msal_app.return_value.acquire_token_silent_with_error = Mock(
            return_value=msal_cache_token_response
        )
        msal_app.return_value.acquire_token_by_device_flow = (
            mock_msal_acquire_token_by_device_flow
        )
        yield


@pytest_asyncio.fixture(name="mock_client")
async def mock_client_fixture(
    httpx_mock: HTTPXMock,
    model_instances_response: dict[str, Any],
    patch_liminal_api_server: None,
    patch_msal: None,
) -> AsyncGenerator[Client]:
    """Return a fixture for a Liminal client.

    Args:
    ----
        httpx_mock: The HTTPX mock fixture.
        model_instances_response: The model instances response.
        patch_liminal_api_server: Ensure the Liminal API server is patched.
        patch_msal: Ensure the MSAL library is patched.

    Returns:
    -------
        A fixture for a Liminal client.

    """
    microsoft_auth_provider = DeviceCodeFlowProvider(TEST_TENANT_ID, TEST_CLIENT_ID)
    async with httpx.AsyncClient(timeout=DEFAULT_REQUEST_TIMEOUT) as httpx_client:
        client = await Client.authenticate_from_auth_provider(
            TEST_API_SERVER_URL, microsoft_auth_provider, httpx_client=httpx_client
        )
        yield client


@pytest.fixture(name="msal_accounts")
def msal_accounts_fixture() -> list[Mock]:
    """Return a fixture for MSAL accounts.

    Returns
    -------
        A fixture for MSAL accounts.

    """
    return []


@pytest.fixture(name="mock_msal_acquire_token_by_device_flow")
def mock_msal_acquire_token_by_device_flow_fixture(
    msal_token_by_device_flow_response: dict[str, Any],
) -> Mock:
    """Return a mocked version of the MSAL acquire_token_by_device_flow method.

    Args:
    ----
        msal_token_by_device_flow_response: The MSAL acquire_token_by_device_flow
            method.

    Returns:
    -------
        A mocked version of the MSAL acquire_token_by_device_flow method.

    """
    return Mock(return_value=msal_token_by_device_flow_response)


@pytest.fixture(name="msal_cache_token_response", scope="session")
def msal_cache_token_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL cache token response.

    Returns
    -------
        A fixture for an MSAL cache token response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("msal-cache-token-response.json")),
    )


@pytest.fixture(name="msal_token_by_device_flow_response", scope="session")
def msal_token_by_device_flow_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL token by device flow response.

    Returns
    -------
        A fixture for an MSAL token by device flow response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("msal-token-by-device-flow-response.json")),
    )


@pytest.fixture(name="model_instances_response", scope="session")
def model_instances_response_fixture() -> dict[str, Any]:
    """Return a fixture for a model instances response.

    Returns
    -------
        A fixture for a model instances response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("model-instances-response.json"))
    )


@pytest.fixture(name="prompt_analyze_response", scope="session")
def prompt_analyze_response_fixture() -> dict[str, Any]:
    """Return a fixture for an analyze response.

    Returns
    -------
        A fixture for an analyze response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("prompt-analyze-response.json"))
    )


@pytest.fixture(name="prompt_cleanse_response", scope="session")
def prompt_cleanse_response_fixture() -> dict[str, Any]:
    """Return a fixture for an cleanse response.

    Returns
    -------
        A fixture for an cleanse response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("prompt-cleanse-response.json"))
    )


@pytest.fixture(name="prompt_hydrate_response", scope="session")
def prompt_hydrate_response_fixture() -> dict[str, Any]:
    """Return a fixture for an hydrate response.

    Returns
    -------
        A fixture for an hydrate response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("prompt-hydrate-response.json"))
    )


@pytest.fixture(name="prompt_stream_response", scope="session")
def prompt_stream_response_fixture() -> str:
    """Return a fixture for a prompt stream response.

    Returns
    -------
        A fixture for a prompt stream iterator.

    """
    return load_fixture("prompt-stream-response.txt")


@pytest.fixture(name="prompt_stream_response_iterator", scope="session")
def prompt_stream_response_iterator_fixture(
    prompt_stream_response: str, request: pytest.FixtureRequest
) -> IteratorStream:
    """Return a fixture for a prompt stream iterator.

    Args:
    ----
        prompt_stream_response: The prompt stream response.
        request: The pytest request object.

    Returns:
    -------
        A fixture for a prompt stream iterator.

    """
    if param := request.param.values[0]:
        return param

    chunks = prompt_stream_response.split(" ")
    output = []
    for index, text in enumerate(chunks):
        raw_chunk: dict[str, Any] = {"content": text}
        if index != len(chunks) - 1:
            raw_chunk["finishReason"] = None
        else:
            raw_chunk["finishReason"] = "stop"
        output.append(f"{json.dumps(raw_chunk)}\n".encode())
    return IteratorStream(output)


@pytest.fixture(name="prompt_submit_response", scope="session")
def prompt_submit_response_fixture() -> dict[str, Any]:
    """Return a fixture for a prompt submit response.

    Returns
    -------
        A fixture for a prompt submit response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("prompt-submit-response.json")))


@pytest.fixture(name="threads_create_response", scope="session")
def threads_create_response_fixture() -> dict[str, Any]:
    """Return a fixture for a threads create response.

    Returns
    -------
        A fixture for a threads create response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("threads-create-response.json"))
    )


@pytest.fixture(name="threads_get_available_response", scope="session")
def threads_get_available_fixture_response() -> dict[str, Any]:
    """Return a fixture for an available threads response.

    Returns
    -------
        A fixture for an available threads response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("threads-get-available-response.json"))
    )


@pytest.fixture(name="threads_get_by_id_response", scope="session")
def threads_get_by_id_response_fixture() -> dict[str, Any]:
    """Return a fixture for a thread-by-id response.

    Returns
    -------
        A fixture for a thread-by-id response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("threads-get-by-id-response.json"))
    )


@pytest.fixture(
    name="threads_get_deidentified_context_history_response", scope="session"
)
def get_deidentified_context_history_response_fixture() -> dict[str, Any]:
    """Return a fixture for a thread's deidentified context history response.

    Returns
    -------
        A fixture for a thread's deidentified context history response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("threads-deidentified-context-history-response.json")),
    )
