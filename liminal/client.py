"""Define the client module."""
# pylint: disable=too-many-arguments
from datetime import datetime

import msgspec
from httpx import AsyncClient, Cookies, HTTPStatusError, Request, Response

from liminal.const import LOGGER
from liminal.endpoints.auth import AuthProvider
from liminal.endpoints.llm import LLMEndpoint
from liminal.endpoints.prompt import PromptEndpoint
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
        self._refresh_token: str | None = None
        self._refreshing_access_token = False

        # Define endpoints:
        self.llm = LLMEndpoint(self._request_and_validate)
        self.prompt = PromptEndpoint(self._request_and_validate)
        self.thread = ThreadEndpoint(self._request, self._request_and_validate)

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        cookies: Cookies | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> Response:
        """Make a request to the Liminal API server and return a Response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
            An HTTPX Response object.
        """
        if (
            not self._refreshing_access_token
            and self._access_token_expires_at
            and datetime.utcnow() >= self._access_token_expires_at
        ):
            LOGGER.debug("Access token expired, refreshing...")
            self._refreshing_access_token = True
            await self.authenticate_from_refresh_token()

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

        request = Request(
            method, url, headers=headers, cookies=cookies, params=params, json=json
        )
        response = await client.send(request)

        try:
            response.raise_for_status()
        except HTTPStatusError as err:
            response_body = err.response.json()
            raise RequestError(
                f"Error while sending request to {url}: "
                f"{response_body.get('error', 'Unknown')}"
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
        cookies: Cookies | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> ValidatedResponseT:
        """Make a request to the Liminal API server and validate the response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
            A validated response object.
        """
        response = await self._request(
            method, endpoint, headers=headers, cookies=cookies, params=params, json=json
        )

        try:
            return msgspec.json.decode(response.content, type=expected_response_type)
        except msgspec.ValidationError as err:
            raise RequestError(f"Could not validate response: {err}") from err

    def _save_tokens_from_auth_response(self, auth_response: Response) -> None:
        """Save tokens from an auth response."""
        LOGGER.debug("Saving tokens from auth response")
        self._access_token = auth_response.cookies["accessToken"]
        # self._access_token_expires_at = datetime.fromtimestamp(
        #     int(auth_response.cookies["accessTokenExpiresAt"]) / 1000
        # )
        self._access_token_expires_at = datetime.fromtimestamp(0)
        self._refresh_token = auth_response.cookies["refreshToken"]

    async def authenticate_from_auth_provider(self) -> None:
        """Authenticate with the Liminal API server (using the auth provider)."""
        provider_access_token = await self._auth_provider.get_access_token()
        liminal_auth_response = await self._request(
            "GET",
            "/v1/auth/login/oauth/access-token",
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )
        self._save_tokens_from_auth_response(liminal_auth_response)

    async def authenticate_from_refresh_token(
        self, *, refresh_token: str | None = None
    ) -> None:
        """Authenticate with the Liminal API server (using a refresh token)."""
        if refresh_token is None and self._refresh_token is None:
            raise AuthError("No valid refresh token provided")

        if refresh_token:
            # If a refresh token is explicitly provided, use it:
            self._refresh_token = refresh_token

        assert self._refresh_token is not None

        refresh_token_response = await self._request(
            "POST",
            "/v1/auth/refresh-token",
            cookies=Cookies({"refreshToken": self._refresh_token}),
        )
        self._save_tokens_from_auth_response(refresh_token_response)
