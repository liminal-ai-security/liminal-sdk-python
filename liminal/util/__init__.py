"""Define utilities."""
from typing import Any, cast

import jwt


def decode_jwt(encoded_jwt: str) -> dict[str, Any]:
    """Decode a JWT."""
    return cast(
        dict[str, Any],
        jwt.decode(
            encoded_jwt,
            "secret",
            algorithms=["HS256"],
            options={"verify_signature": False},
        ),
    )
