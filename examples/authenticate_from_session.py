"""Define a simple example."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("authenticate_from_session")


async def main() -> None:
    """Create the aiohttp session and run the example."""
    logging.basicConfig(level=logging.INFO)

    try:
        client_id = os.environ["CLIENT_ID"]
        liminal_api_server_url = os.environ["LIMINAL_API_SERVER_URL"]
        tenant_id = os.environ["TENANT_ID"]
    except KeyError as err:
        msg = (
            "Please set the LIMINAL_API_SERVER_URL, CLIENT_ID, and TENANT_ID "
            "environment variables"
        )
        raise LiminalError(msg) from err

    # Create an auth provider to authenticate the user:
    microsoft_auth_provider = DeviceCodeFlowProvider(tenant_id, client_id)

    # Create the liminal SDK instance:
    liminal = Client(microsoft_auth_provider, liminal_api_server_url)

    try:
        saved_session = None

        def save_session(session: str) -> None:
            """Save the session."""
            nonlocal saved_session
            saved_session = session

        liminal.add_session_callback(save_session)

        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()

        # Authenticate from session:
        await liminal.authenticate_from_session(session=saved_session)
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
