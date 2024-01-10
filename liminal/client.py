"""Define the client module."""
# pylint: disable=too-many-arguments
from datetime import datetime

import msgspec
from httpx import AsyncClient, HTTPStatusError, Request, Response

from liminal.const import LOGGER
from liminal.endpoints.auth import AuthProvider
from liminal.endpoints.auth.models import LiminalTokenResponse
from liminal.endpoints.auth.util import decode_jwt
from liminal.endpoints.llm import LLMEndpoint
from liminal.endpoints.thread import ThreadEndpoint
from liminal.errors import AuthError, RequestError
from liminal.helpers.typing import ValidatedResponseT

DEFAULT_REQUEST_TIMEOUT = 60
DEFAULT_SOURCE = "SDK"


class Client:
    """Define the client class."""

    def __init__(
        self,
        auth_provider: AuthProvider,
        api_server_url: str,
        *,
        source: str = DEFAULT_SOURCE,
        httpx_client: AsyncClient | None = None,
    ) -> None:
        """Initialize.

        Args:
            auth_provider: The instantiated auth provider to use.
            api_server_url: The URL of the Liminal API server.
            source: The source of the SDK.
            httpx_client: An optional HTTPX client to use.
        """
        self._api_server_url = api_server_url
        self._auth_provider = auth_provider
        self._httpx_client = httpx_client
        self._source = source

        # Token information will be filled in by authenticate():
        self._access_token: str | None = None
        self._access_token_expires_at: datetime | None = None

        # Define endpoints:
        self.llm = LLMEndpoint(self._request_and_validate)
        self.thread = ThreadEndpoint(self._request_and_validate)

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> Response:
        """Make a request to the Liminal API server and return a Response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
            An HTTPX Response object.
        """
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{self._api_server_url}{endpoint}"

        if not headers:
            headers = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        if not params:
            params = {}
        params["source"] = self._source

        if running_client := self._httpx_client and not self._httpx_client.is_closed:
            client = self._httpx_client
        else:
            client = AsyncClient()

        request = Request(method, url, headers=headers, params=params, json=json)
        response = await client.send(request)

        try:
            response.raise_for_status()
        except HTTPStatusError as err:
            response_body = err.response.json()
            raise RequestError(
                f"Error while sending request to {url}: {response_body['error']}"
            ) from err

        if not running_client:
            await client.aclose()

        LOGGER.debug("Received data from %s: %s", url, response.content)

        return response

    async def _request_and_validate(
        self,
        method: str,
        endpoint: str,
        expected_response_type: type[ValidatedResponseT],
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> ValidatedResponseT:
        """Make a request to the Liminal API server and validate the response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
            A validated response object.
        """
        response = await self._request(
            method, endpoint, headers=headers, params=params, json=json
        )

        try:
            return msgspec.json.decode(response.content, type=expected_response_type)
        except msgspec.ValidationError as err:
            raise RequestError(f"Could not validate response: {err}") from err

    async def authenticate(self) -> None:
        """Authenticate with the Liminal API server (using the auth provider)."""
        provider_access_token = await self._auth_provider.get_access_token()
        liminal_auth_response: LiminalTokenResponse = await self._request_and_validate(
            "GET",
            "/login/oauth/access_code",
            LiminalTokenResponse,
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )

        if liminal_auth_response.message != "Authenticated":
            raise AuthError(f"Authentication failed: {liminal_auth_response.message}")

        token = liminal_auth_response.token
        decoded_jwt = decode_jwt(token)
        self._access_token = token
        self._access_token_expires_at = datetime.fromtimestamp(decoded_jwt["exp"])
