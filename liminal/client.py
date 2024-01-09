"""Define the client module."""
from datetime import datetime
from typing import Any

from httpx import AsyncClient, HTTPStatusError, Request

from liminal.auth import AuthProvider
from liminal.const import LOGGER
from liminal.errors import AuthError, RequestError
from liminal.util import decode_jwt

DEFAULT_REQUEST_TIMEOUT = 60
DEFAULT_SOURCE = "SDK"


class Client:
    """Define the client class."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        auth_provider: AuthProvider,
        api_server_url: str,
        *,
        source: str = DEFAULT_SOURCE,
        llm_service_model_key: str | None = None,
        httpx_client: AsyncClient | None = None,
    ) -> None:
        """Initialize.

        Args:
            auth_provider: The instantiated auth provider to use.
            api_server_url: The URL of the Liminal API server.
            source: The source of the SDK.
            llm_service_model_key: A key denoting which LLM to use.
            httpx_client: An optional HTTPX client to use.
        """
        self._api_server_url = api_server_url
        self._auth_provider = auth_provider
        self._httpx_client = httpx_client
        self._llm_service_model_key = llm_service_model_key
        self._source = source

        # Token information will be filled in by authenticate():
        self._access_token: str | None = None
        self._access_token_expires_at: datetime | None = None

    async def _request(  # pylint: disable=too-many-arguments
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Liminal API server."""
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{self._api_server_url}{endpoint}"

        if running_client := self._httpx_client and not self._httpx_client.is_closed:
            client = self._httpx_client
        else:
            client = AsyncClient()

        request = Request(method, url, headers=headers, params=params, data=data)
        response = await client.send(request)

        try:
            response.raise_for_status()
        except HTTPStatusError as err:
            raise RequestError(err.response.json()) from err

        json: dict[str, Any] = response.json()

        if not running_client:
            await client.aclose()

        LOGGER.debug("Received data from %s: %s", url, data)

        return json

    async def authenticate(self) -> None:
        """Authenticate with the Liminal API server (using the auth provider)."""
        provider_access_token = await self._auth_provider.get_access_token()
        liminal_auth_response = await self._request(
            "GET",
            "/login/oauth/access_code",
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )

        if liminal_auth_response.get("message") != "Authenticated":
            raise AuthError(
                f"Authentication failed: {liminal_auth_response['message']}"
            )

        token = liminal_auth_response["token"]
        decoded_jwt = decode_jwt(token)
        self._access_token = token
        self._access_token_expires_at = datetime.fromtimestamp(decoded_jwt["exp"])

        print(self._access_token)
        print(self._access_token_expires_at)
