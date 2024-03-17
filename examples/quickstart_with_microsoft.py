"""Define a quickstart example."""

import asyncio
import logging
import os

from liminal import Client
from liminal.endpoints.auth import MicrosoftAuthProvider
from liminal.errors import LiminalError

_LOGGER = logging.getLogger("quickstart_with_microsoft")


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

        # Get available model instances:
        model_instances = await liminal.llm.get_available_model_instances()
        _LOGGER.info("Available Model Instances: %s", model_instances)

        # Get the model instance:
        model_instance = await liminal.llm.get_model_instance(MODEL_INSTANCE_NAME)

        # Create a thread using the designated model instance
        created_thread = await liminal.thread.create(model_instance.id, "My thread")
        _LOGGER.info("Created thread: %s", created_thread)

        # Get all available threads:
        available_threads = await liminal.thread.get_available()
        _LOGGER.info("Available threads: %s", available_threads)

        # Get a thread by ID:
        retrieved_thread = await liminal.thread.get_by_id(created_thread.id)
        _LOGGER.info("Retrieved thread: %s", retrieved_thread)

        # Analyze a prompt and  get "findings" (details on detected sensitive info):
        prompt = (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        )
        findings = await liminal.prompt.analyze(retrieved_thread.id, prompt)
        _LOGGER.info("Analysis findings: %s", findings)

        # Send a prompt to an LLM and get a response (choosing to include the findings
        # and deidentified context history we've already retrieved):
        response = await liminal.prompt.submit(
            created_thread.id,
            prompt,
            findings=findings,
        )
        _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
