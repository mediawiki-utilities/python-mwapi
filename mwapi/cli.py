"""
Command-line Interface (cli)
============================

This module provides utilities for interacting with a user from the
command-line.

.. autofunction:: mwapi.cli.do_login
"""
import getpass
import sys

from .errors import ClientInteractionRequest


def do_login(session, for_what):
    """
    Performs a login handshake with a user on the command-line.  This method
    will handle all of the follow-up requests (e.g. capcha or two-factor).  A
    login that requires two-factor looks like this::

        >>> import mwapi.cli
        >>> import mwapi
        >>> mwapi.cli.do_login(mwapi.Session("https://en.wikipedia.org"), "English Wikipedia")
        Log into English Wikipedia
        Username: Halfak (WMF)
        Passord:
        Please enter verification code from your mobile app
        Token(OATHToken): 234567

    :Parameters:
        session : :class:`mwapi.Session`
            A session object to use for login
        for_what : `str`
            A name to display to the use (for what they are logging into)
    """  # noqa
    username, password = request_username_password(for_what)
    try:
        session.login(username, password)
    except ClientInteractionRequest as cir:
        params = request_interaction(cir)
        session.continue_login(cir.login_token, **params)


def request_interaction(cir):
    sys.stderr.write("{0}\n".format(cir.message))

    params = {}
    for req_doc in cir.requests:
        # sys.stderr.write("id: {0}\n".format(req_doc['id']))
        for name, field in req_doc['fields'].items():
            prefix = "{0}({1}): ".format(field['label'], name)
            if field.get('sensitive', False):
                value = getpass.getpass(prefix)
            else:
                sys.stderr.write(prefix)
                sys.stderr.flush()
                value = open('/dev/tty').readline().strip()

            params[name] = value

    return params


def request_username_password(for_what):
    sys.stderr.write("Log into " + for_what + "\n")
    sys.stderr.write("Username: ")
    sys.stderr.flush()
    return open('/dev/tty').readline().strip(), getpass.getpass("Password: ")
