"""Define package exceptions."""


class LiminalError(Exception):
    """Define a base exception."""

    pass


class RequestError(LiminalError):
    """Define an exception related to an HTTP request."""

    pass


class AuthError(RequestError):
    """Define an exception related to invalid auth."""

    pass
