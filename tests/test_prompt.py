"""Define prompt endpoint tests."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from liminal import Client
from tests.common import TEST_API_SERVER_URL


@pytest.mark.asyncio()
async def test_analyze(
    httpx_mock: HTTPXMock, mock_client: Client, prompt_analyze_response: dict[str, Any]
) -> None:
    """Test the analyze endpoint.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        prompt_analyze_response: An analyze response.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/analyze_response?source=sdk",
        json=prompt_analyze_response,
    )

    findings = await mock_client.prompt.analyze(
        123,
        (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        ),
    )
    assert len(findings.findings) == 5


@pytest.mark.asyncio()
async def test_cleanse_and_hydrate(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    prompt_analyze_response: dict[str, Any],
    prompt_cleanse_response: dict[str, Any],
    prompt_hydrate_response: dict[str, Any],
) -> None:
    """Test the cleanse endpoint.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        prompt_analyze_response: An analyze response.
        prompt_cleanse_response: A cleanse response.
        prompt_hydrate_response: A hydrate response.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/analyze_response?source=sdk",
        json=prompt_analyze_response,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/cleanse_response?source=sdk",
        json=prompt_cleanse_response,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/hydrate_response?source=sdk",
        json=prompt_hydrate_response,
    )

    findings = await mock_client.prompt.analyze(
        123,
        (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        ),
    )
    assert len(findings.findings) == 5

    cleansed = await mock_client.prompt.cleanse(
        123,
        (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        ),
        findings=findings,
    )
    assert len(cleansed.items) == 5
    assert len(cleansed.items_hashed) == 5
    assert cleansed.text == (
        "Write a short marketing email for a banking customer PERSON_0, whose email "
        "address is EMAIL_ADDRESS_0 and who lives at LOCATION_0. PERSON_1 was born on "
        "DATE_0 and identifies as Female"
    )

    hydrated = await mock_client.prompt.hydrate(
        123, "Tell PERSON_0 that we are grateful for their business."
    )
    assert len(hydrated.items) == 1
    assert hydrated.text == (
        "Tell Jane Gansbuhler that we are grateful for their business."
    )


@pytest.mark.asyncio()
async def test_submit(
    httpx_mock: HTTPXMock,
    mock_client: Client,
    prompt_analyze_response: dict[str, Any],
    prompt_submit_response: dict[str, Any],
) -> None:
    """Test the submit endpoint.

    Args:
        httpx_mock: The HTTPX mock fixture.
        mock_client: A mock Liminal client.
        prompt_analyze_response: An analyze response.
        prompt_submit_response: A submit response.

    """
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/analyze_response?source=sdk",
        json=prompt_analyze_response,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{TEST_API_SERVER_URL}/api/v1/sdk/process?source=sdk",
        json=prompt_submit_response,
    )

    findings = await mock_client.prompt.analyze(
        123,
        (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        ),
    )
    assert len(findings.findings) == 5

    response = await mock_client.prompt.submit(
        123,
        (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        ),
        findings=findings,
    )

    # This is a simple test to ensure the data parsed as appropriate:
    assert len(response.deidentified_input_text_data.items_hashed) == 5