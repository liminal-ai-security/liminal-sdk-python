"""Define an example of authenticating with an API token (provided by Liminal)."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("authenticate_from_token")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        liminal_api_server_url = os.environ["LIMINAL_API_SERVER_URL"]
        token = os.environ["TOKEN"]
    except KeyError as err:
        msg = "Please set the LIMINAL_API_SERVER_URL and TOKEN environment variables"
        raise LiminalError(msg) from err

    try:
        # Authenticate from session:
        liminal = await Client.authenticate_from_token(liminal_api_server_url, token)

        # Get available model instances:
        model_instances = await liminal.llm.get_available_model_instances()
        _LOGGER.info("Available Model Instances: %s", model_instances)
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
