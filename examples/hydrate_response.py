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
DEMO_MODEL = "gpt-4-1106-preview"


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
            (x for x in available_llms if x.model == DEMO_MODEL), None
        )
        if retrieved_elements:
            model_instance_id = retrieved_elements.id

        # Create a thread using GPT-4:
        created_thread = await liminal.thread.create(model_instance_id, "My thread")
        _LOGGER.info("Created thread: %s", created_thread)

        # Analyze a prompt and  get "findings" (details on detected sensitive info):
        prompt = (
            "Write a short marketing email for a banking customer Jane Gansbuhler, "
            "whose email address is egansbuhler0@pinterest.com and who lives at 14309 "
            "Lindbergh Circle Alexander City Alabama. Jane was born on 6/5/1961 and "
            "identifies as Female"
        )

        findings = await liminal.prompt.analyze(created_thread.id, prompt)
        _LOGGER.info("Analysis findings: %s", findings)

        cleansed_prompt = await liminal.prompt.cleanse(
            created_thread.id,
            prompt,
        )
        _LOGGER.info("Cleansed response: %s", cleansed_prompt)

        # TODO: new prompt here that contains the analysis findings cleansed keywords

        # Rehydrate my cleansed prompt after I have done something with the text
        hydrated_response = await liminal.prompt.hydrate(
            created_thread.id,
            cleansed_prompt.text,
        )
        _LOGGER.info("Hydrated response: %s", hydrated_response)

        # Send a prompt to an LLM and get a response (choosing to include the findings
        # and deidentified context history we've already retrieved):
        # response = await liminal.prompt.submit(
        #     created_thread.id,
        #     prompt,
        #     findings=findings,
        # )
        # _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
