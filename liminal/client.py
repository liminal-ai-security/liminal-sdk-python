"""Define the client module."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from json.decoder import JSONDecodeError
from typing import Any, Final

from httpx import AsyncClient, Cookies, HTTPStatusError, Response
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
from liminal.errors import RequestError
from liminal.helpers.typing import ValidatedResponseT

DEFAULT_REQUEST_TIMEOUT: Final[int] = 60


class Client:
    """Define the client class."""

    def __init__(
        self,
        api_server_url: str,
        *,
        httpx_client: AsyncClient | None = None,
    ) -> None:
        """Initialize.

        Args:
        ----
            api_server_url: The URL of the Liminal API server.
            httpx_client: An optional HTTPX client to use.

        """
        self._api_server_url = api_server_url
        self._httpx_client = httpx_client

        # Token information:
        self._session_id: str | None = None

        # Define endpoints:
        self.llm = LLMEndpoint(self._request_and_validate)
        self.prompt = PromptEndpoint(self._request_and_validate, self._stream)
        self.thread = ThreadEndpoint(self._request_and_validate)

    @classmethod
    async def authenticate_from_auth_provider(
        cls,
        api_server_url: str,
        auth_provider: AuthProvider,
        *,
        httpx_client: AsyncClient | None = None,
    ) -> Client:
        """Authenticate with the Liminal API server (using the auth provider).

        Args:
        ----
            api_server_url: The URL of the Liminal API server.
            auth_provider: The auth provider to use.
            httpx_client: An optional HTTPX client to use.

        Returns:
        -------
            A new client instance.

        """
        client = cls(api_server_url, httpx_client=httpx_client)
        provider_access_token = await auth_provider.get_access_token()
        liminal_auth_response = await client._request(  # noqa: SLF001
            "GET",
            "/api/v1/auth/login/oauth/access-token",
            headers={"Authorization": f"Bearer {provider_access_token}"},
        )
        client._save_session_id_from_auth_response(liminal_auth_response)  # noqa: SLF001
        return client

    @classmethod
    async def authenticate_from_session_id(
        cls,
        api_server_url: str,
        session_id: str,
        *,
        httpx_client: AsyncClient | None = None,
    ) -> Client:
        """Authenticate with the Liminal API server (using a session).

        Args:
        ----
            api_server_url: The URL of the Liminal API server.
            httpx_client: An optional HTTPX client to use.
            session_id: The session ID to use. If not provided, the session that was
                used to authenticate the user initially will be used.

        Returns:
        -------
            A new client instance.

        """
        client = cls(api_server_url, httpx_client=httpx_client)
        session_id_response = await client._request(  # noqa: SLF001
            "GET", "/api/v1/users/me", cookies={"session": session_id}
        )
        client._save_session_id_from_auth_response(session_id_response)  # noqa: SLF001
        return client

    @classmethod
    async def authenticate_from_token(
        cls,
        api_server_url: str,
        token: str,
        *,
        httpx_client: AsyncClient | None = None,
    ) -> Client:
        """Authenticate with the Liminal API server (using a Liminal-provided token).

        Args:
        ----
            api_server_url: The URL of the Liminal API server.
            token: The token to use.
            httpx_client: An optional HTTPX client to use.

        """
        client = cls(api_server_url, httpx_client=httpx_client)
        liminal_auth_response = await client._request(  # noqa: SLF001
            "POST",
            "/api/v1/auth/test-automation/login",
            headers={"x-test-automation-api-key": token},
        )
        client._save_session_id_from_auth_response(liminal_auth_response)  # noqa: SLF001
        return client

    @property
    def session_id(self) -> str | None:
        """Return the session ID.

        Returns
        -------
            The session ID.

        """
        return self._session_id

    def _create_cookie_jar(self, raw_cookies: dict[str, Any] | None) -> Cookies:
        """Create a cookie jar from raw cookies.

        Args:
        ----
            raw_cookies: The raw cookies to use.

        Returns:
        -------
            A cookie jar.

        """
        if not raw_cookies:
            raw_cookies = {}
        if self._session_id:
            raw_cookies["session"] = self._session_id
        return Cookies(raw_cookies)

    @asynccontextmanager
    async def _get_httpx_client(self) -> AsyncIterator[AsyncClient]:
        """Get an HTTPX client.

        Returns
        -------
            An HTTPX client.

        """
        if running_client := self._httpx_client and not self._httpx_client.is_closed:
            client = self._httpx_client
        else:
            client = AsyncClient(timeout=DEFAULT_REQUEST_TIMEOUT)

        yield client

        if not running_client:
            await client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        """Make a request to the Liminal API server and return a response.

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
        cookie_jar = self._create_cookie_jar(cookies)

        async with self._get_httpx_client() as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                cookies=cookie_jar,
                params=params,
                json=json,
                timeout=DEFAULT_REQUEST_TIMEOUT,
            )

            try:
                response.raise_for_status()
            except HTTPStatusError as err:
                msg = (
                    f"Error while sending request to {url}: "
                    f"{err.response.content.decode()}"
                )
                raise RequestError(msg) from err

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
        json: dict[str, Any] | None = None,
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

    async def _stream(
        self,
        method: str,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """Make a request to the Liminal API server and return a streaming response.

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
            An AsyncIterator containing the raw JSON response chunks.

        """
        url = f"{self._api_server_url}{endpoint}"
        cookie_jar = self._create_cookie_jar(cookies)

        # pylint: disable=contextmanager-generator-missing-cleanup
        async with (
            self._get_httpx_client() as client,
            client.stream(
                method,
                url,
                headers=headers,
                cookies=cookie_jar,
                params=params,
                json=json,
            ) as resp,
        ):
            async for line in resp.aiter_lines():
                LOGGER.info("Received line of streaming response: %s", line)
                yield line
