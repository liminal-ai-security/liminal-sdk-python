"""Define dynamic test fixtures."""

from __future__ import annotations

from collections.abc import Generator
import json
from time import time
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
from pytest_httpx import HTTPXMock

from tests.common import TEST_API_SERVER_URL, load_fixture


@pytest.fixture(name="patch_liminal_api_server")
def _patch_liminal_api_server_fixture(httpx_mock: HTTPXMock) -> None:
    """Patch the Liminal API server.

    Args:
        httpx_mock: The HTTPX mock fixture.

    """
    httpx_mock.add_response(
        method="GET",
        url=f"{TEST_API_SERVER_URL}/api/v1/auth/login/oauth/access-token?source=sdk",
        headers=[
            ("Set-Cookie", "accessToken=REDACTED"),
            ("Set-Cookie", f"accessTokenExpiresAt={(int(time()) + 3600) * 1000}"),
            ("Set-Cookie", "refreshToken=REDACTED"),
        ],
    )


@pytest.fixture(name="patch_msal")
def _patch_msal_fixture(
    msal_cache_token_response: dict[str, Any],
    msal_token_by_device_flow_response: dict[str, Any],
) -> Generator[None, None, None]:
    """Patch the MSAL library.

    Args:
        msal_cache_token_response: The MSAL cache token response.
        msal_token_by_device_flow_response: The MSAL token by device flow response.

    Yields:
        None.

    """
    with patch("liminal.endpoints.auth.PublicClientApplication") as msal_app:
        msal_app.return_value.get_accounts = Mock(return_value=[Mock()])
        msal_app.return_value.initiate_device_flow = Mock(
            return_value={
                "message": (
                    "To sign in, use a web browser to open the page https://microsoft.com/devicelogin "
                    "and enter the code ABCD12345 to authenticate."
                )
            }
        )
        msal_app.return_value.acquire_token_silent_with_error = Mock(
            return_value=msal_cache_token_response
        )
        msal_app.return_value.acquire_token_by_device_flow = Mock(
            return_value=msal_token_by_device_flow_response
        )
        yield


@pytest.fixture(name="analyze_response", scope="session")
def analyze_response_fixture() -> dict[str, Any]:
    """Return a fixture for an analyze response.

    Returns:
        A fixture for an analyze response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("analyze-response.json")))


@pytest.fixture(name="msal_cache_token_response", scope="session")
def msal_cache_token_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL cache token response.

    Returns:
        A fixture for an MSAL cache token response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("msal_cache_token_response.json")),
    )


@pytest.fixture(name="msal_token_by_device_flow_response", scope="session")
def msal_token_by_device_flow_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL token by device flow response.

    Returns:
        A fixture for an MSAL token by device flow response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("msal_token_by_device_flow_response.json")),
    )


@pytest.fixture(name="model_instances_response", scope="session")
def model_instances_response_fixture() -> dict[str, Any]:
    """Return a fixture for a model instances response.

    Returns:
        A fixture for a model instances response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("model-instances-response.json"))
    )


@pytest.fixture(name="prompt_response", scope="session")
def prompt_response_fixture() -> dict[str, Any]:
    """Return a fixture for a prompt response.

    Returns:
        A fixture for a prompt response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("prompt-response.json")))


@pytest.fixture(name="thread_by_id_response", scope="session")
def thread_by_id_response_fixture() -> dict[str, Any]:
    """Return a fixture for a thread-by-id response.

    Returns:
        A fixture for a thread-by-id response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("thread-by-id-response.json")))


@pytest.fixture(name="threads_response", scope="session")
def threads_response_fixture() -> dict[str, Any]:
    """Return a fixture for a threads response.

    Returns:
        A fixture for a threads response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("threads-response.json")))
