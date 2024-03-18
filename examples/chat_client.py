"""Define a chat client example."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("chat_client")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        client_id = os.environ["CLIENT_ID"]
        liminal_api_server_url = os.environ["LIMINAL_API_SERVER_URL"]
        model_instance_name = os.environ["MODEL_INSTANCE_NAME"]
        tenant_id = os.environ["TENANT_ID"]
    except KeyError as err:
        msg = "Please set the LIMINAL_API_SERVER_URL, CLIENT_ID, TENANT_ID, and MODEL_INSTANCE_NAME environment variables"
        raise LiminalError(msg) from err

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider(tenant_id, client_id)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, liminal_api_server_url)

    try:
        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()
    except LiminalError:
        _LOGGER.exception("Error during authentication")

    try:
        # Get the model instance:
        model_instance = await liminal.llm.get_model_instance(model_instance_name)

        # Create Thread and begin prompts
        created_thread = await liminal.thread.create(model_instance.id, "Demo Thread")
        while True:
            if (prompt := input("Enter a message: ")) == "quit":
                break

            findings = await liminal.prompt.analyze(created_thread.id, prompt)
            _LOGGER.info("Analysis findings: %s", findings)

            response = await liminal.prompt.submit(
                created_thread.id, prompt, findings=findings
            )
            _LOGGER.info("LLM response: %s", response)
    except LiminalError:
        _LOGGER.exception("Error while running example")


asyncio.run(main())
