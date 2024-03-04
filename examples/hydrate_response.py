"""Define a simple example."""
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
DEMO_MODEL_NAME = "My Model Instance"


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

        # Get available LLMs:
        available_llms = await liminal.llm.get_available_model_instances()
        _LOGGER.info("Available LLMs: %s", available_llms)

        # Get model instance id
        model_instance_id = -1
        retrieved_elements = next(
            (x for x in available_llms if x.name == DEMO_MODEL_NAME), None
        )
        if retrieved_elements:
            model_instance_id = retrieved_elements.id
        else:
            raise LiminalError(
                "Please make sure the following model instance name exists before "
                "attempting to run this example script: " + str(DEMO_MODEL_NAME)
            )

        # Create a thread with your designated model instance:
        created_thread = await liminal.thread.create(model_instance_id, "My thread")
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
