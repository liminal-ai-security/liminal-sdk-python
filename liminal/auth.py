"""Define helpers for the auth client service."""
import asyncio
from abc import ABC
from typing import cast

from msal import PublicClientApplication

from liminal.const import LOGGER
from liminal.errors import LiminalError

DEFAULT_AUTH_CHALLENGE_TIMEOUT = 60


class AuthServiceError(LiminalError):
    """Define an error related to the auth client service."""

    pass


class AuthFailedError(AuthServiceError):
    """Define an error related to authentication failure."""

    pass


class AuthProvider(ABC):
    """Define an auth provider abstract base class."""

    async def get_access_token(self) -> str:
        """Retrieve an access token from the auth provider.

        The working principle here is that the auth provider will return an access
        token that can be used to authenticate with the Liminal API server.

        Returns:
            The access token.
        """
        raise NotImplementedError


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
                return cast(str, result["access_token"])

        LOGGER.debug("No cached access token found; generating a new one")

        flow = self._msal_app.initiate_device_flow(scopes=self.DEFAULT_SCOPES)
        LOGGER.info(flow["message"])

        try:
            async with asyncio.timeout(self._auth_challenge_timeout):
                fut = self._loop.run_in_executor(
                    None, self._msal_app.acquire_token_by_device_flow, flow
                )
                result = await fut
        except asyncio.TimeoutError as err:
            flow["expires_at"] = 0
            raise AuthFailedError(
                "Timed out waiting for authentication challenge"
            ) from err

        return cast(str, result["access_token"])
