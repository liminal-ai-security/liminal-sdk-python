"""Define a chat client example."""

import asyncio
import logging
import os

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("chat_client")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        CLIENT_ID = os.environ["CLIENT_ID"]
        LIMINAL_API_SERVER_URL = os.environ["LIMINAL_API_SERVER_URL"]
        MODEL_INSTANCE = os.environ["MODEL_INSTANCE"]
        TENANT_ID = os.environ["TENANT_ID"]
    except KeyError as err:
        raise LiminalError(
            "Please set the LIMINAL_API_SERVER_URL, CLIENT_ID, TENANT_ID, and "
            "MODEL_INSTANCE environment variables"
        ) from err

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
        # Get model instance:
        model_instances = await liminal.llm.get_available_model_instances()
        try:
            model_instance = next(
                instance
                for instance in model_instances
                if instance.name == MODEL_INSTANCE
            )
        except StopIteration as err:
            raise LiminalError(
                f"Unknown model instance name: {MODEL_INSTANCE}"
            ) from err

        if model_instance.model_connection is None:
            raise LiminalError(f"Unknown model instance name: {MODEL_INSTANCE}")

        # Create Thread and begin prompts:
        created_thread = await liminal.thread.create(model_instance.id, "Chat Example")

        while True:
            if (prompt := input("Enter a message: ")) == "quit":
                break

            findings = await liminal.prompt.analyze(created_thread.id, prompt)
            _LOGGER.info("Analysis findings: %s", findings)

            response = await liminal.prompt.submit(
                created_thread.id, prompt, findings=findings
            )
            _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error while running example: %s", err)


asyncio.run(main())
