"""Define auth providers."""


class AuthProvider:  # pylint: disable=too-few-public-methods
    """Define an auth provider abstract base class."""

    async def get_access_token(self) -> str:
        """Retrieve an access token from the auth provider.

        The working principle here is that the auth provider will return an access
        token that can be used to authenticate with the Liminal API server.

        Returns
        -------
            The access token.

        """
        raise NotImplementedError
