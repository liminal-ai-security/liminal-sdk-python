"""Define a simple example."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("hydrate_response")


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

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, liminal_api_server_url)

    try:
        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()

        # Get the model instance:
        model_instance = await liminal.llm.get_model_instance(model_instance_name)

        # Create a thread with your designated model instance:
        created_thread = await liminal.thread.create(model_instance.id, "My thread")
        _LOGGER.info("Created thread: %s", created_thread)

        # Analyze a prompt and  get "findings" (details on detected sensitive info):
        prompt = input(
            "Enter a prompt you would like to be cleansed of sensitive info: "
        )

        findings = await liminal.prompt.analyze(model_instance.id, prompt)
        _LOGGER.info("Analysis findings: %s", findings)

        cleansed_prompt = await liminal.prompt.cleanse(
            model_instance.id,
            prompt,
            thread_id=created_thread.id,
        )
        _LOGGER.info("Cleansed response: %s", cleansed_prompt)

        prompt_to_hydrate = input(
            "Enter a prompt (using the masked terms from the cleansed prompt above) "
            "that you would like to have rehydrated with the sensitive "
            "info that was previously cleansed: "
        )

        # Rehydrate my cleansed prompt after I have done something with the text
        hydrated_response = await liminal.prompt.hydrate(
            model_instance.id, prompt_to_hydrate, thread_id=created_thread.id
        )
        _LOGGER.info("Hydrated response: %s", hydrated_response)
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
