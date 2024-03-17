"""Define models for the auth endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from liminal.helpers.model import BaseModel


class AuthProvider:
    """Define an auth provider abstract base class."""

    async def get_access_token(self) -> str:
        """Retrieve an access token from the auth provider.

        The working principle here is that the auth provider will return an access
        token that can be used to authenticate with the Liminal API server.

        Returns:
            The access token.

        """
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True)
class MSALCacheTokenResponse(BaseModel):
    """Define an MSAL token response from Entra ID."""

    token_type: Literal["Bearer"]
    access_token: str
    expires_in: int
    token_source: Literal["cache"]


@dataclass(frozen=True, kw_only=True)
class MSALIdentityProviderTokenResponse(BaseModel):
    """Define an MSAL token response from the local in-memory cache."""

    token_type: Literal["Bearer"]
    scope: str
    expires_in: int
    ext_expires_in: int
    access_token: str
    refresh_token: str
    id_token: str
    client_info: str
    id_token_claims: dict
    token_source: Literal["identity_provider"]
