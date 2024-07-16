"""Define a quickstart example."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("authenticate_from_auth_provider")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        client_id = os.environ["CLIENT_ID"]
        liminal_api_server_url = os.environ["LIMINAL_API_SERVER_URL"]
        model_instance_name = os.environ["MODEL_INSTANCE_NAME"]
        tenant_id = os.environ["TENANT_ID"]
    except KeyError as err:
        msg = (
            "Please set the LIMINAL_API_SERVER_URL, CLIENT_ID, TENANT_ID, and "
            "MODEL_INSTANCE_NAME environment variables"
        )
        raise LiminalError(msg) from err

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = DeviceCodeFlowProvider(tenant_id, client_id)

    try:
        # Create the liminal SDK instance:
        liminal = await Client.authenticate_from_auth_provider(
            liminal_api_server_url, microsoft_auth_provider
        )

        # Get available model instances:
        model_instances = await liminal.llm.get_available_model_instances()
        _LOGGER.info("Available Model Instances: %s", model_instances)

        # Get the model instance:
        model_instance = await liminal.llm.get_model_instance(model_instance_name)

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
        findings = await liminal.prompt.analyze(model_instance.id, prompt)
        _LOGGER.info("Analysis findings: %s", findings)

        # Send a prompt to an LLM and get a response (choosing to include the findings
        # and deidentified context history we've already retrieved):
        response = await liminal.prompt.submit(
            model_instance.id,
            prompt,
            findings=findings,
            thread_id=created_thread.id,
        )
        _LOGGER.info("LLM response: %s", response)
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
