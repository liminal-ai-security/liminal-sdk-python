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
        available_llms = await liminal.llm.get_available()
        _LOGGER.info("Available LLMs: %s", available_llms)

        # Create a thread using GPT-4:
        created_thread = await liminal.thread.create("openai_4", "My thread")
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

        # Cleanse a prompt (choosing to include the findings we've already retrieved):
        cleansed_prompt = await liminal.prompt.cleanse(
            retrieved_thread.id, prompt, findings=findings
        )
        _LOGGER.info("Cleansed prompt: %s", cleansed_prompt)

        # Send a prompt to an LLM and get a response (choosing to include the findings
        # and deidentified context history we've already retrieved):
        response = await liminal.prompt.submit(
            retrieved_thread.id, prompt, findings=findings
        )
        _LOGGER.info("LLM response: %s", response)
    except LiminalError as err:
        _LOGGER.error("Error running the script: %s", err)


asyncio.run(main())
