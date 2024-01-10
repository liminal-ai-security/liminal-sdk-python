"""Define a simple example."""
import asyncio
import logging
import os

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("example")

API_SERVER_URL = os.environ["API_SERVER_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    # Create an auth provider to authenticate the user
    microsoft_auth_provider = MicrosoftAuthProvider(TENANT_ID, CLIENT_ID)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, API_SERVER_URL)

    try:
        # Authenticate the user:
        await liminal.authenticate()

        # Get available LLMs:
        available_llms = await liminal.llm.get_available()
        _LOGGER.info("Available LLMs: %s", available_llms)

        # Get available threads:
        available_threads = await liminal.thread.get_available()
        _LOGGER.info("Available threads: %s", available_threads)

        # Create a thread using GPT-4:
        created_thread = await liminal.thread.create("openai_4", "My thread")
        _LOGGER.info("Created thread: %s", created_thread)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
