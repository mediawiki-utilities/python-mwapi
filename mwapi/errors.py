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
    def __init__(self, code, info, content):
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
