"""Define Microsoft providers."""

from __future__ import annotations

import asyncio
from typing import Final

from msal import PublicClientApplication

from liminal.auth import AuthProvider
from liminal.auth.microsoft.models import (
    MSALCacheTokenResponse,
    MSALIdentityProviderTokenResponse,
)
from liminal.const import LOGGER
from liminal.errors import AuthError

DEFAULT_AUTH_CHALLENGE_TIMEOUT: Final[int] = 60


class DeviceCodeFlowProvider(AuthProvider):  # pylint: disable=too-few-public-methods
    """Define a Microsoft auth provider."""

    AUTHORITY_URL: Final[str] = "https://login.microsoftonline.com"
    DEFAULT_SCOPES: Final[list[str]] = ["User.Read"]

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        *,
        auth_challenge_timeout: int = DEFAULT_AUTH_CHALLENGE_TIMEOUT,
    ) -> None:
        """Initialize.

        Args:
        ----
            tenant_id: The Entra ID tenant ID.
            client_id: The Entra ID client ID.
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

        Returns
        -------
            The access token.

        Raises
        ------
            AuthError: If authentication fails.

        """
        if accounts := self._msal_app.get_accounts():  # noqa: SIM102
            if result := self._msal_app.acquire_token_silent_with_error(
                self.DEFAULT_SCOPES, account=accounts[0]
            ):
                LOGGER.debug("Retrieved access token from existing cache")
                cached_response = MSALCacheTokenResponse.from_dict(result)
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
            msg = "Timed out waiting for authentication challenge"
            raise AuthError(msg) from err

        identity_provider_response = MSALIdentityProviderTokenResponse.from_dict(result)
        return identity_provider_response.access_token
