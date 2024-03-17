"""Define dynamic test fixtures."""

import json
from typing import Any, cast

import pytest

from tests.common import load_fixture


@pytest.fixture(name="analyze_response", scope="session")
def analyze_response_fixture() -> dict[str, Any]:
    """Return a fixture for an analyze response.

    Returns:
        A fixture for an analyze response.

    """
    return cast(dict[str, Any], json.loads(load_fixture("analyze-response.json")))


@pytest.fixture(name="microsoft_cache_event_response", scope="session")
def microsoft_cache_event_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL cache event response.

    Returns:
        A fixture for an MSAL cache event response.

    """
    return cast(
        dict[str, Any], json.loads(load_fixture("microsoft_cache_event_response.json"))
    )


@pytest.fixture(name="microsoft_openid_config_response", scope="session")
def microsoft_openid_config_response_fixture() -> dict[str, Any]:
    """Return a fixture for an MSAL OpenID config response.

    Returns:
        A fixture for an MSAL OpenID config response.

    """
    return cast(
        dict[str, Any],
        json.loads(load_fixture("microsoft_openid_config_response.json")),
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
