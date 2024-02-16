"""Define a chat client example."""
import asyncio
import logging
import os

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("example")

LIMINAL_API_SERVER_URL = os.environ["LIMINAL_API_SERVER_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider(TENANT_ID, CLIENT_ID)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, LIMINAL_API_SERVER_URL)

    try:
        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()
    except LiminalError as err:
        _LOGGER.error("Error authenticating: %s", err)

    try:
        while True:
            if (prompt := input("Enter a message: ")) == "quit":
                break

            created_thread = await liminal.thread.create("openai_35", "Demo Thread")

            findings = await liminal.prompt.analyze(created_thread.id, prompt)
            _LOGGER.info("Analysis findings: %s", findings)
            _LOGGER.info("")

            cleansed_prompt = await liminal.prompt.cleanse(
                created_thread.id, prompt, findings=findings
            )
            _LOGGER.info("Cleansed prompt: %s", cleansed_prompt)
            _LOGGER.info("")

            response = await liminal.prompt.submit(
                created_thread.id, prompt, findings=findings
            )
            _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error while running example: %s", err)


asyncio.run(main())
