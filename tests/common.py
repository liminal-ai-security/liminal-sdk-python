"""Define common test utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Final

TEST_API_SERVER_URL: Final[str] = "https://api.domain.liminal.ai"
TEST_CLIENT_ID: Final[str] = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
TEST_HTTPX_DEFAULT_TIMEOUT: Final[int] = 10
TEST_SESSION_ID: Final[str] = "session-id"
TEST_TENANT_ID: Final[str] = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
TEST_TOKEN: Final[str] = "token"  # noqa: S105


def load_fixture(filename: str) -> str:
    """Load a fixture.

    Args:
    ----
        filename: The filename of the fixtures/ file to load.

    Returns:
    -------
        A string containing the contents of the file.

    """
    path = Path(f"{Path(__file__).parent}/fixtures/{filename}")
    with Path.open(path, encoding="utf-8") as fptr:
        return fptr.read()
