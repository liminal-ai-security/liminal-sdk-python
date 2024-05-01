"""Define a simple example."""

import asyncio
import logging
import os
from typing import Final

from liminal import Client
from liminal.auth.microsoft.device_code_flow import DeviceCodeFlowProvider
from liminal.errors import LiminalError

_LOGGER: Final[logging.Logger] = logging.getLogger("authenticate_from_session_cookie")


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
        saved_session_cookie = None

        def save_session_cookie(session_cookie: str) -> None:
            """Save the session cookie."""
            nonlocal saved_session_cookie
            saved_session_cookie = session_cookie

        liminal.add_session_cookie_callback(save_session_cookie)

        # Authenticate the user:
        await liminal.authenticate_from_auth_provider()

        # Authenticate from session:
        await liminal.authenticate_from_session_cookie(
            session_cookie=saved_session_cookie
        )
    except LiminalError:
        _LOGGER.exception("Error running the script")


asyncio.run(main())
