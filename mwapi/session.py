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

    def __init__(self, host, user_agent=None, api_path=None,
                 timeout=None, session=None):
        self.host = str(host)
        self.api_path = str(api_path or "/w/api.php")
        self.api_url = self.host + self.api_path
        self.timeout = float(timeout) if timeout is not None else None
        self.session = session or requests.Session()
        self.headers = {}

        if user_agent is None:
            logger.warning("Sending requests with default User-Agent.  " +
                           "Set 'user_agent' on mwapi.Session to quiet this " +
                           "message.")
            self.headers['User-Agent'] = DEFAULT_USERAGENT
        else:
            self.headers['User-Agent'] = user_agent

    def _request(self, method, params=None, data=None, files=None):
        try:
            resp = self.session.request(method, self.api_url, params=params,
                                        data=data, files=files,
                                        timeout=self.timeout, headers=self.headers,
                                        stream=True)
        except requests.exceptions.Timeout as e:
            raise TimeoutError(str(e))
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(str(e))
        except requests.exceptions.HTTPError as e:
            raise HTTPError(str(e))
        except requests.exceptions.TooManyRedirects as e:
            raise TooManyRedirectsError(str(e))
        except requests.exceptions.RequestException as e:
            raise RequestError(str(e))
        except Exception as e:
            raise RequestError(str(e))

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
        else:
            return doc

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

    def get(self, query_continue=None, **params):
        """Makes an API request with the GET method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
            params :
                Keyword parameters to be sent in the query string.

        :Raises:
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """
        return self._request('GET', self._normalize_params(params))

    def post(self, query_continue=None, upload_file=None, **params):
        """Makes an API request with the POST method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
            upload_file : `bytes`
                The bytes of a file to upload.
            params :
                Keyword parameters to be sent in the POST message body.

        :Raises:
            :class:`mwapi.errors.APIError` : if the API responds with an error
        """

        kwargs = {'data': self._normalize_params(params)}
        if upload_file is not None:
            kwargs['files'] = {'file': upload_file}

        return self._request('POST', **kwargs)

    def _normalize_params(self, params, query_continue=None):
        for key, value in params.items():
            if isinstance(value, str):
                pass
            elif hasattr(value, "__iter__"):
                params[key] = "|".join(str(v) for v in value)

        if query_continue is not None:
            params.update(query_continue)

        params['format'] = 'json'

        return params
