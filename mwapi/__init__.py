"""
MediaWiki API
=============

This library provides a set of basic utilities for interacting with MediaWiki's
"action" API -- usually available at /w/api.php.  The most salient feature of
this library is the :class:`~mwapi.session.Session` class that provides a
connection session that sustains a logged-in user status and provides
convenience functions for calling the MediaWiki API -- for example,
:func:`~mwapi.session.Session.get`, :func:`~mwapi.session.Session.post`, and
:func:`~mwapi.session.Session.login`.

Authors
=======
* YuviPanda https://github.com/yuvipanda

Contributing
++++++++++++
* Aaron Halfaker https://github.com/halfak
"""
import requests
from .session import Session

MWApi = Session
