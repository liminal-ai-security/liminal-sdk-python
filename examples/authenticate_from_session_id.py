"""Define an example of authenticating with a Liminal API server session."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("authenticate_from_session_id")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        liminal_api_server_url = os.environ["LIMINAL_API_SERVER_URL"]
        session_id = os.environ["SESSION_ID"]
    except KeyError as err:
        msg = (
            "Please set the LIMINAL_API_SERVER_URL and SESSION_ID environment variables"
        )
        raise LiminalError(msg) from err

    try:
        # Authenticate from session:
        liminal = await Client.authenticate_from_session_id(
            liminal_api_server_url, session_id
        )

        # Get available model instances:
        model_instances = await liminal.llm.get_available_model_instances()
        _LOGGER.info("Available Model Instances: %s", model_instances)
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
