"""
This library provides a set of basic utilities for interacting with MediaWiki's
"action" API -- usually available at /w/api.php.  The most salient feature of
this library is the `Session` class that provides a
connection session that sustains a logged-in user status and provides
convenience functions for calling the MediaWiki API -- for example,
`get()`, `post()`, and `login()`.

:Authors:
    * YuviPanda https://github.com/yuvipanda
    * Aaron Halfaker https://github.com/halfak

:License: MIT
"""
from .session import Session


MWApi = Session

__all__ = [MWApi, Session]

__version__ = "0.4.1"
