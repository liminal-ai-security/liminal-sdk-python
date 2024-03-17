"""Define package exceptions."""


class LiminalError(Exception):
    """Define a base exception."""


class RequestError(LiminalError):
    """Define an exception related to an HTTP request."""


class AuthError(RequestError):
    """Define an exception related to invalid auth."""


class ModelInstanceUnknownError(RequestError):
    """Define an exception related to an unknown model instance."""
