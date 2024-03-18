"""Define common test utilities."""

from __future__ import annotations

from pathlib import Path

TEST_API_SERVER_URL = "https://api.domain.liminal.ai"
TEST_CLIENT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
TEST_TENANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"


def load_fixture(filename: str) -> str:
    """Load a fixture.

    Args:
        filename: The filename of the fixtures/ file to load.

    Returns:
        A string containing the contents of the file.

    """
    path = Path(f"{Path(__file__).parent}/fixtures/{filename}")
    with Path.open(path, encoding="utf-8") as fptr:
        return fptr.read()
