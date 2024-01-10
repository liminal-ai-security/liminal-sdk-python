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

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider(TENANT_ID, CLIENT_ID)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, API_SERVER_URL)

    try:
        # Authenticate the user:
        await liminal.authenticate()

        # Get available LLMs:
        available_llms = await liminal.llm.get_available()
        _LOGGER.info("Available LLMs: %s", available_llms)

        # Create a thread using GPT-4:
        created_thread = await liminal.thread.create("openai_4", "My thread")
        _LOGGER.info("Created thread: %s", created_thread)

        # Get a thread by ID:
        retrieved_thread = await liminal.thread.get_by_id(created_thread.id)
        _LOGGER.info("Retrieved thread: %s", retrieved_thread)

        # Get all available threads:
        available_threads = await liminal.thread.get_available()
        _LOGGER.info("Available threads: %s", available_threads)

        # Delete a thread by ID:
        await liminal.thread.delete_by_id(retrieved_thread.id)
        _LOGGER.info("Deleted thread: %s", retrieved_thread)

        # Analyze a prompt:
        prompt = (
            "Write a personalized marketing email for a banking customer Jane "
            "Gansbuhler, whose email address is egansbuhler0@pinterest.com and "
            "who lives at 14309 Lindbergh Circle Alexander City Alabama. Jane "
            "was born on 6/5/1961 and identifies as Female"
        )
        findings = await liminal.prompt.analyze(prompt)
        _LOGGER.info("Analysis findings: %s", findings)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
