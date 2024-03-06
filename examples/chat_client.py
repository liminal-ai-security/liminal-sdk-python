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
DEMO_MODEL = "gpt-3.5-turbo"


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
        # Get model instance id
        model_instances = await liminal.llm.get_available_model_instances()
        model_instance_id = -1
        retrieved_elements = next(
            (x for x in model_instances if x.model == DEMO_MODEL), None
        )
        if retrieved_elements:
            model_instance_id = retrieved_elements.id
        else:
            raise LiminalError(
                "Please make sure to connect the following model before attempting "
                "to run this example script: {DEMO_MODEL}"
            )

        # Create Thread and begin prompts
        created_thread = await liminal.thread.create(model_instance_id, "Demo Thread")
        while True:
            if (prompt := input("Enter a message: ")) == "quit":
                break

            findings = await liminal.prompt.analyze(created_thread.id, prompt)
            _LOGGER.info("Analysis findings: %s", findings)
            _LOGGER.info("")

            response = await liminal.prompt.submit(
                created_thread.id, prompt, findings=findings
            )
            _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error while running example: %s", err)


asyncio.run(main())
