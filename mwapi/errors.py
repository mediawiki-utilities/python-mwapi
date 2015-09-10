"""
Errors
======

.. autoclass:: APIError

.. autoclass:: LoginError

.. autoclass:: RequestError

.. autoclass:: ConnectionError

.. autoclass:: HTTPError

.. autoclass:: TooManyRedirectsError

.. autoclass:: TimeoutError
"""
import requests.exceptions


class APIError(RuntimeError):
    """
    Thrown when the MediaWiki API returns an error.
    """
    def __init__(self, code, info, content):
        super().__init__((code, info, content))
        self.code = code
        self.info = info
        self.content = content

        super().__init__("{0}: {1} -- {2}".format(code, info, content))

    @classmethod
    def from_doc(cls, doc):
        return cls(
            doc.get('code'),
            doc.get('info'),
            doc.get('*')
        )


class LoginError(RuntimeError):
    """
    Thrown when an error occurs during login.
    """

    @classmethod
    def from_doc(cls, doc):
        return cls(doc.get('result'))


class RequestError(requests.exceptions.RequestException):
    """
    A generic error thrown by :mod:`requests`.
    """
    pass


class ConnectionError(requests.exceptions.ConnectionError):
    """
    Handles a :class:`requests.exceptions.ConnectionError`
    """
    pass


class HTTPError(requests.exceptions.HTTPError):
    """
    Handles a :class:`requests.exceptions.HTTPError`
    """
    pass


class TooManyRedirectsError(requests.exceptions.TooManyRedirects):
    """
    Handles a :class:`requests.exceptions.TooManyRedirects`
    """
    pass


class TimeoutError(requests.exceptions.Timeout):
    """
    Handles a :class:`requests.exceptions.TimeoutError`
    """
    pass
