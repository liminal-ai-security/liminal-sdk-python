"""Define the client module."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Final

from httpx import AsyncClient, Cookies, HTTPStatusError, Request, Response
from mashumaro.codecs.json import json_decode
from mashumaro.exceptions import (
    MissingField,
    SuitableVariantNotFoundError,
    UnserializableDataError,
)

from liminal.const import LOGGER
from liminal.endpoints.auth import AuthProvider
from liminal.endpoints.llm import LLMEndpoint
from liminal.endpoints.prompt import PromptEndpoint
from liminal.endpoints.thread import ThreadEndpoint
from liminal.errors import AuthError, RequestError
from liminal.helpers.typing import ValidatedResponseT

DEFAULT_REQUEST_TIMEOUT: Final[int] = 60
DEFAULT_SOURCE: Final[str] = "sdk"


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

        # Token information:
        self._access_token: str | None = None
        self._access_token_expires_at: datetime | None = None
        self._refresh_event = asyncio.Event()
        self._refresh_lock = asyncio.Lock()
        self._refresh_token: str | None = None
        self._refresh_token_callbacks: list[Callable[[str], None]] = []
        self._refreshing = False

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
        refresh_request: bool = False,
    ) -> Response:
        """Make a request to the Liminal API server and return a Response.

        Args:
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.
            refresh_request: Whether or not this request is a refresh request.

        Returns:
            An HTTPX Response object.

        Raises:
            RequestError: If the response fails for any reason.

        """
        utcnow = datetime.now(tz=UTC)
        if self._access_token_expires_at and utcnow >= self._access_token_expires_at:
            LOGGER.debug("Access token expired, refreshing...")
            self._access_token = None
            self._access_token_expires_at = None
            await self.authenticate_from_refresh_token()

        # If an authenticated request arrives while we're refreshing, hold until the
        # refresh process is done:
        if not refresh_request and self._refreshing:
            await self._refresh_event.wait()

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
            msg = (
                f"Error while sending request to {url}: {err.response.content.decode()}"
            )
            raise RequestError(msg) from err

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
            expected_response_type: The expected type of the response.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
            A validated response object.

        Raises:
            RequestError: If the response could not be validated.

        """
        response = await self._request(
            method, endpoint, headers=headers, cookies=cookies, params=params, json=json
        )

        try:
            return json_decode(response.content, expected_response_type)
        except (
            MissingField,
            SuitableVariantNotFoundError,
            UnserializableDataError,
        ) as err:
            msg = f"Could not validate response: {err}"
            raise RequestError(msg) from err

    def _save_tokens_from_auth_response(self, auth_response: Response) -> None:
        """Save tokens from an auth response.

        Args:
            auth_response: The response from an auth request.

        """
        LOGGER.debug("Saving tokens from auth response")
        self._access_token = auth_response.cookies["accessToken"]
        self._access_token_expires_at = datetime.fromtimestamp(
            int(auth_response.cookies["accessTokenExpiresAt"]) / 1000, tz=UTC
        )
        self._refresh_token = auth_response.cookies["refreshToken"]

        for callback in self._refresh_token_callbacks:
            callback(self._refresh_token)

    def add_refresh_token_callback(
        self, callback: Callable[[str], None]
    ) -> Callable[[], None]:
        """Add a callback to be called when a new refresh token is generated.

        The purpose of this is to allow the user to save the refresh token to a
        persistent store using their own callback method.

        Args:
            callback: The callback to add.

        Returns:
            A method to cancel and remove the callback.

        """
        self._refresh_token_callbacks.append(callback)

        def cancel() -> None:
            """Cancel and remove the callback."""
            self._refresh_token_callbacks.remove(callback)

        return cancel

    async def authenticate_from_auth_provider(self) -> None:
        """Authenticate with the Liminal API server (using the auth provider)."""
        provider_access_token = await self._auth_provider.get_access_token()
        liminal_auth_response = await self._request(
            "GET",
            "/api/v1/auth/login/oauth/access-token",
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )
        self._save_tokens_from_auth_response(liminal_auth_response)

    async def authenticate_from_refresh_token(
        self, *, refresh_token: str | None = None
    ) -> None:
        """Authenticate with the Liminal API server (using a refresh token).

        Args:
            refresh_token: The refresh token to use. If not provided, the refresh token
                that was used to authenticate the user initially will be used.

        Raises:
            AuthError: If no refresh token is provided and the user has not been
                authenticated yet.

        """
        if not refresh_token:
            refresh_token = self._refresh_token

        if not refresh_token:
            msg = "No valid refresh token provided"
            raise AuthError(msg)

        self._refreshing = True

        async with self._refresh_lock:
            self._refresh_event.clear()

            try:
                refresh_token_response = await self._request(
                    "POST",
                    "/api/v1/auth/refresh-token",
                    refresh_request=True,
                    cookies=Cookies({"refreshToken": refresh_token}),
                )
                self._save_tokens_from_auth_response(refresh_token_response)
            finally:
                self._refreshing = False
                self._refresh_event.set()
