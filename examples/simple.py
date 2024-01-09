"""Define a simple example."""
import asyncio
import logging
import os

from liminal import Client, MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("example")

API_SERVER_URL = os.environ["API_SERVER_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.DEBUG)

    # Create an auth provider to authenticate the user
    microsoft_auth_provider = MicrosoftAuthProvider(TENANT_ID, CLIENT_ID)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, API_SERVER_URL)

    try:
        # Authenticate the user:
        await liminal.authenticate()
    except LiminalError as err:
        _LOGGER.error("Error while authenticating: %s", err)


asyncio.run(main())
