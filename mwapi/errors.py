"""
Errors
======
There's two types of errors.

.. autoclass:: APIError

.. autoclass:: LoginError
"""


class APIError(RuntimeError):
    """
    Thrown when the MediaWiki API returns an error.
    """
    pass


class LoginError(APIError):
    """
    Thrown when an error occurs during login.
    """
    pass
