"""Define the auth endpoint."""

import asyncio
import json

import msgspec
from msal import PublicClientApplication

from liminal.const import LOGGER
from liminal.errors import LiminalError

from .models import (
    AuthProvider,
    MSALCacheTokenResponse,
    MSALIdentityProviderTokenResponse,
)

DEFAULT_AUTH_CHALLENGE_TIMEOUT = 60


class AuthServiceError(LiminalError):
    """Define an error related to the auth client service."""


class AuthFailedError(AuthServiceError):
    """Define an error related to authentication failure."""


class MicrosoftAuthProvider(AuthProvider):
    """Define a Microsoft auth provider."""

    AUTHORITY_URL = "https://login.microsoftonline.com"
    DEFAULT_SCOPES = ["User.Read"]

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        *,
        auth_challenge_timeout: int = DEFAULT_AUTH_CHALLENGE_TIMEOUT,
    ) -> None:
        """Initialize.

        Args:
            auth_challenge_timeout: How long (in seconds) before aborting an auth
                challenge.
        """
        self._auth_challenge_timeout = auth_challenge_timeout
        self._loop = asyncio.get_event_loop()
        self._msal_app = PublicClientApplication(
            client_id=client_id, authority=f"{self.AUTHORITY_URL}/{tenant_id}"
        )

    async def get_access_token(self) -> str:
        """Retrieve an access token from Microsoft Entra ID (via MSAL).

        Returns:
            The access token.

        Raises:
            AuthFailedError: If authentication fails.
        """
        if accounts := self._msal_app.get_accounts():
            if result := self._msal_app.acquire_token_silent_with_error(
                self.DEFAULT_SCOPES, account=accounts[0]
            ):
                LOGGER.debug("Retrieved access token from existing cache")
                cached_response = msgspec.json.decode(
                    json.dumps(result), type=MSALCacheTokenResponse
                )
                return cached_response.access_token

        LOGGER.debug("No cached access token found; generating a new one")

        flow = self._msal_app.initiate_device_flow(scopes=self.DEFAULT_SCOPES)
        LOGGER.info(flow["message"])

        try:
            async with asyncio.timeout(self._auth_challenge_timeout):
                fut = self._loop.run_in_executor(
                    None, self._msal_app.acquire_token_by_device_flow, flow
                )
                result = await fut
        except TimeoutError as err:
            # Setting the flow to expire immediately will effectively kill the future
            # that we're awaiting:
            flow["expires_at"] = 0
            raise AuthFailedError(
                "Timed out waiting for authentication challenge"
            ) from err

        identity_provider_response = msgspec.json.decode(
            json.dumps(result), type=MSALIdentityProviderTokenResponse
        )
        return identity_provider_response.access_token
