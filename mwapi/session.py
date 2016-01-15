"""
Session
=======

Sessions encapsulate a a set of interactions with a MediaWiki API.
:class:`mwapi.Session` provides both a set of convenience functions (e.g.
:func:`~mwapi.Session.get` and :func:`~mwapi.Session.post`) that
automatically convert parameters and handle error code responses and raise
them as exceptions.  You can also maintain a logged-in connection to the
API by using :func:`~mwapi.Session.login` to authenticate and using the
same session call :func:`~mwapi.Session.get` and :func:`~mwapi.Session.post`
afterwards.

.. autoclass:: mwapi.Session
    :members:
"""
import logging

import requests
import requests.exceptions

from .errors import (APIError, ConnectionError, HTTPError, LoginError,
                     RequestError, TimeoutError, TooManyRedirectsError)

DEFAULT_USERAGENT = "mwapi (python) -- default user-agent"

logger = logging.getLogger(__name__)


class Session:
    """
    Constructs a new API session.

    :Parameters:
        host : `str`
            Host to which to connect to. Must include http:// or https:// and
            no trailing "/".
        user_agent : `str`
            The User-Agent header to include with all requests.  Use this field
            to identify your script/bot/application to system admins of the
            MediaWiki API you are using.
        formatversion : int
            The formatversion to supply to the API for all requests.
        api_path : `str`
            The path to "api.php" on the server -- must begin with "/".
        timeout : `float`
            How long to wait for the server to send data before giving up
            and raising an error (:class:`requests.exceptions.Timeout`,
            :class:`requests.exceptions.ReadTimeout` or
            :class:`requests.exceptions.ConnectTimeout`).  The default behavior
            is to hang indefinitely.
        session : `requests.Session`
            (optional) a `requests` session object to use
    """

    def __init__(self, host, user_agent=None, formatversion=None,
                 api_path=None,
                 timeout=None, session=None, **session_params):
        self.host = str(host)
        self.formatversion = int(formatversion) if formatversion is not None \
                             else None
        self.api_path = str(api_path or "/w/api.php")
        self.api_url = self.host + self.api_path
        self.timeout = float(timeout) if timeout is not None else None
        self.session = session or requests.Session()
        for key, value in session_params.items():
            setattr(self.session, key, value)

        self.headers = {}

        if user_agent is None:
            logger.warning("Sending requests with default User-Agent.  " +
                           "Set 'user_agent' on mwapi.Session to quiet this " +
                           "message.")
            self.headers['User-Agent'] = DEFAULT_USERAGENT
        else:
            self.headers['User-Agent'] = user_agent

    def _request(self, method, params=None, files=None, auth=None):
        params = params or {}
        if self.formatversion is not None:
            params['formatversion'] = self.formatversion

        if method.lower() == "post":
            data = params
            data['format'] = "json"
            params = None
        else:
            data = None
            params = params or {}
            params['format'] = "json"

        try:
            resp = self.session.request(method, self.api_url, params=params,
                                        data=data, files=files,
                                        timeout=self.timeout,
                                        headers=self.headers,
                                        verify=True,
                                        stream=True,
                                        auth=auth)
        except requests.exceptions.Timeout as e:
            raise TimeoutError(str(e)) from e
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(str(e)) from e
        except requests.exceptions.HTTPError as e:
            raise HTTPError(str(e)) from e
        except requests.exceptions.TooManyRedirects as e:
            raise TooManyRedirectsError(str(e)) from e
        except requests.exceptions.RequestException as e:
            raise RequestError(str(e)) from e
        except Exception as e:
            raise RequestError(str(e)) from e

        try:
            doc = resp.json()
        except ValueError:
            if resp is None:
                prefix = "No response data"
            else:
                prefix = resp.text[:350]
            raise ValueError("Could not decode as JSON:\n{0}"
                             .format(prefix))

        if 'error' in doc:
            raise APIError.from_doc(doc['error'])

        if 'warnings' in doc:
            logger.warning("The following query raised warnings: {0}"
                           .format(params or data))
            for module, warning in doc['warnings'].items():
                logger.warning("\t- {0} -- {1}"
                               .format(module, warning))
        return doc

    def request(self, method, params=None, query_continue=None,
                files=None, auth=None, continuation=False):
        """
        Sends an HTTP request to the API.

        :Parameters:
            method : `str`
                Which HTTP method to use for the request?
                (Usually "POST" or "GET")
            params : `dict`
                A set of parameters to send with the request.  These parameters
                will be included in the POST body for post requests or a query
                string otherwise.
            query_continue : `dict`
                A 'continue' field from a past request.  This field represents
                the point from which a query should be continued.
            files : `dict`
                A dictionary of (filename : `str`, data : `bytes`) pairs to
                send with the request.
            auth : mixed
                Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
            continuation : `bool`
                If true, a continuation will be attempted and a generator of
                JSON response documents will be returned.

        :Returns:
            A response JSON documents (or a generator of documents if
            `continuation == True`)
        """
        normal_params = _normalize_params(params, query_continue)
        if continuation:
            return self._continuation(method, params=normal_params, auth=auth,
                                      files=files)
        else:
            return self._request(method, params=normal_params, auth=auth,
                                 files=files)

    def continuation(self, method, params=None, query_continue=None,
                     auth=None, files=None):
        """
        Makes a request and, if the response calls for a continuation,
        performs that continuation.

        :Parameters:
            method : `str`
                Which HTTP method to use for the request?
                (Usually "POST" or "GET")
            params : `dict`
                A set of parameters to send with the request.  These parameters
                will be included in the POST body for post requests or a query
                string otherwise.
            files : `dict`
                A dictionary of (filename : `str`, data : `bytes`) pairs to
                send with the initial request.
            auth : mixed
                Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
            query_continue : `dict`
                A 'continue' field from a past request.  This field represents
                the point from which a query should be continued.

        :Returns:
            A generator of response JSON documents.
        """

    def _continuation(self, method, params=None, files=None, auth=None):
        if 'continue' not in params:
            params['continue'] = ''

        while True:
            doc = self._request(method, params=params, files=files, auth=None)
            yield doc
            if 'continue' not in doc:
                break
            # re-send all continue values in the next call
            params.update(doc['continue'])
            files = None  # Don't send files again

    def login(self, username, password):
        """
        Authenticate with the given credentials.  If authentication is
        successful, all further requests sent will be signed the authenticated
        user.

        Note that passwords are sent as plaintext. This is a limitation of the
        Mediawiki API.  Use a https host if you want your password to be secure

        :Parameters:
            username : str
                The username of the user to be authenticated
            password : str
                The password of the user to be authenticated

        :Raises:
            :class:`mwapi.errors.LoginError` : if authentication fails
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """
        token_doc = self.post(action="login", lgname=username,
                              lgpassword=password)

        login_doc = self.post(action="login", lgname=username,
                              lgpassword=password,
                              lgtoken=token_doc['login']['token'])

        result = login_doc['login']['result']
        if result != 'Success':
            raise LoginError.from_doc(login_doc['login'])
        return result

    def logout(self):
        """
        Logs out of the session with MediaWiki

        :Raises:
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """
        self.post(action='logout')

    def get(self, query_continue=None, auth=None, continuation=False,
            **params):
        """Makes an API request with the GET method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
            auth : mixed
                Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
            continuation : `bool`
                If true, a continuation will be attempted and a generator of
                JSON response documents will be returned.
            params :
                Keyword parameters to be sent in the query string.

        :Returns:
            A response JSON documents (or a generator of documents if
            `continuation == True`)

        :Raises:
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """

        return self.request('GET', params=params, auth=auth,
                            query_continue=query_continue,
                            continuation=continuation)

    def post(self, query_continue=None, upload_file=None, auth=None,
             continuation=False, **params):
        """Makes an API request with the POST method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
            upload_file : `bytes`
                The bytes of a file to upload.
            auth : mixed
                Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
            continuation : `bool`
                If true, a continuation will be attempted and a generator of
                JSON response documents will be returned.
            params :
                Keyword parameters to be sent in the POST message body.

        :Returns:
            A response JSON documents (or a generator of documents if
            `continuation == True`)

        :Raises:
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """
        if upload_file is not None:
            files = {'file': upload_file}
        else:
            files = None

        return self.request('POST', params=params, auth=auth,
                            query_continue=query_continue, files=files,
                            continuation=continuation)


def _normalize_value(value):
    if isinstance(value, str):
        return value
    elif hasattr(value, "__iter__"):
        return "|".join(str(v) for v in value)
    else:
        return value


def _normalize_params(params, query_continue=None):
    normal_params = {k: _normalize_value(v) for k, v in params.items()}

    if query_continue is not None:
        normal_params.update(query_continue)

    return normal_params
