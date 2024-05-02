"""Define the client module."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from json.decoder import JSONDecodeError
from typing import Final

from httpx import AsyncClient, Cookies, HTTPStatusError, Request, Response
from mashumaro.codecs.json import json_decode
from mashumaro.exceptions import (
    MissingField,
    SuitableVariantNotFoundError,
    UnserializableDataError,
)

from liminal.auth import AuthProvider
from liminal.const import LOGGER
from liminal.endpoints.llm import LLMEndpoint
from liminal.endpoints.prompt import PromptEndpoint
from liminal.endpoints.thread import ThreadEndpoint
from liminal.errors import AuthError, RequestError
from liminal.helpers.typing import ValidatedResponseT

DEFAULT_REQUEST_TIMEOUT: Final[int] = 60


class Client:
    """Define the client class."""

    def __init__(
        self,
        auth_provider: AuthProvider,
        api_server_url: str,
        *,
        httpx_client: AsyncClient | None = None,
    ) -> None:
        """Initialize.

        Args:
        ----
            auth_provider: The instantiated auth provider to use.
            api_server_url: The URL of the Liminal API server.
            httpx_client: An optional HTTPX client to use.

        """
        self._api_server_url = api_server_url
        self._auth_provider = auth_provider
        self._httpx_client = httpx_client

        # Token information:
        self._refresh_lock = asyncio.Lock()
        self._refreshing = False
        self._session_id: str | None = None
        self._session_id_callbacks: list[Callable[[str], None]] = []

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
        cookies: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> Response:
        """Make a request to the Liminal API server and return a Response.

        Args:
        ----
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
        -------
            An HTTPX Response object.

        Raises:
        ------
            RequestError: If the response fails for any reason.

        """
        url = f"{self._api_server_url}{endpoint}"

        if not cookies:
            cookies = {}
        if self._session_id:
            cookies["session"] = self._session_id

        if running_client := self._httpx_client and not self._httpx_client.is_closed:
            client = self._httpx_client
        else:
            client = AsyncClient()

        request = Request(
            method,
            url,
            headers=headers,
            cookies=Cookies(cookies),
            params=params,
            json=json,
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
        cookies: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
    ) -> ValidatedResponseT:
        """Make a request to the Liminal API server and validate the response.

        Args:
        ----
            method: The HTTP method to use.
            endpoint: The endpoint to request.
            expected_response_type: The expected type of the response.
            headers: The headers to use.
            cookies: The cookies to use.
            params: The query parameters to use.
            json: The JSON body to use.

        Returns:
        -------
            A validated response object.

        Raises:
        ------
            RequestError: If the response could not be validated.

        """
        response = await self._request(
            method, endpoint, headers=headers, cookies=cookies, params=params, json=json
        )

        try:
            return json_decode(response.content, expected_response_type)
        except (
            JSONDecodeError,
            MissingField,
            SuitableVariantNotFoundError,
            UnserializableDataError,
        ) as err:
            msg = f"Could not validate response: {err}"
            raise RequestError(msg) from err

    def _save_session_id_from_auth_response(self, auth_response: Response) -> None:
        """Save a session cookie value from an auth response.

        Args:
        ----
            auth_response: The response from an auth request.

        """
        LOGGER.debug("Saving session cookie from auth response")
        self._session_id = auth_response.cookies["session"]

        if self._session_id:
            for callback in self._session_id_callbacks:
                callback(self._session_id)

    def add_session_id_callback(
        self, callback: Callable[[str], None]
    ) -> Callable[[], None]:
        """Add a callback to be called when a new session is generated.

        The purpose of this is to allow the user to save the session ID to a
        persistent store using their own callback method.

        Args:
        ----
            callback: The callback to add.

        Returns:
        -------
            A method to cancel and remove the callback.

        """
        self._session_id_callbacks.append(callback)

        def cancel() -> None:
            """Cancel and remove the callback."""
            self._session_id_callbacks.remove(callback)

        return cancel

    async def authenticate_from_auth_provider(self) -> None:
        """Authenticate with the Liminal API server (using the auth provider)."""
        provider_access_token = await self._auth_provider.get_access_token()
        liminal_auth_response = await self._request(
            "GET",
            "/api/v1/auth/login/oauth/access-token",
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )
        self._save_session_id_from_auth_response(liminal_auth_response)

    async def authenticate_from_session_id(
        self, *, session_id: str | None = None
    ) -> None:
        """Authenticate with the Liminal API server (using a session).

        Args:
        ----
            session_id: The session ID to use. If not provided, the session that was
                used to authenticate the user initially will be used.

        Raises:
        ------
            AuthError: If no session is provided and the user has not been authenticated
                yet.

        """
        if not session_id:
            session_id = self._session_id

        if not session_id:
            msg = "No valid session ID provided"
            raise AuthError(msg)

        async with self._refresh_lock:
            self._refreshing = True

            try:
                session_id_response = await self._request(
                    "GET",
                    "/api/v1/users/me",
                    cookies={"session": session_id},
                )
                self._save_session_id_from_auth_response(session_id_response)
            finally:
                self._refreshing = False
