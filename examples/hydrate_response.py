"""Define a simple example."""

import asyncio
import logging
import os

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("hydrate_response")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        CLIENT_ID = os.environ["CLIENT_ID"]
        LIMINAL_API_SERVER_URL = os.environ["LIMINAL_API_SERVER_URL"]
        MODEL_INSTANCE_NAME = os.environ["MODEL_INSTANCE_NAME"]
        TENANT_ID = os.environ["TENANT_ID"]
    except KeyError as err:
        raise LiminalError(
            "Please set the LIMINAL_API_SERVER_URL, CLIENT_ID, TENANT_ID, and "
            "MODEL_INSTANCE_NAME environment variables"
        ) from err

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = MicrosoftAuthProvider(TENANT_ID, CLIENT_ID)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, LIMINAL_API_SERVER_URL)

    try:
        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()

        # Get the model instance:
        model_instance = await liminal.llm.get_model_instance(MODEL_INSTANCE_NAME)

        # Create a thread with your designated model instance:
        created_thread = await liminal.thread.create(model_instance.id, "My thread")
        _LOGGER.info("Created thread: %s", created_thread)

        # Analyze a prompt and  get "findings" (details on detected sensitive info):
        prompt = input(
            "Enter a prompt you would like to be cleansed of sensitive info: "
        )

        findings = await liminal.prompt.analyze(created_thread.id, prompt)
        _LOGGER.info("Analysis findings: %s", findings)

        cleansed_prompt = await liminal.prompt.cleanse(
            created_thread.id,
            prompt,
        )
        _LOGGER.info("Cleansed response: %s", cleansed_prompt)

        prompt_to_hydrate = input(
            "Enter a prompt (using the masked terms from the cleansed prompt above) "
            "that you would like to have rehydrated with the sensitive "
            "info that was previously cleansed: "
        )

        # Rehydrate my cleansed prompt after I have done something with the text
        hydrated_response = await liminal.prompt.hydrate(
            created_thread.id, prompt_to_hydrate
        )
        _LOGGER.info("Hydrated response: %s", hydrated_response)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
