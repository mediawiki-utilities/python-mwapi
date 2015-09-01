"""
Session
=======

Sessions encapsulate a a set of interactions with a MediaWiki API.
:class:`~mwapi.session.session.Session` provides both a set of convenience
functions (e.g. :func:`~mwapi.session.session.Session.get` and
:func:`~mwapi.session.session.Session.post`) that automatically convert
parameters and handle error code responses and raise them as exceptions.  You
can also maintain a logged-in connection to the API by using
:func:`~mwapi.session.session.Session.login` to authenticate and using the same
session call :func:`~mwapi.session.session.Session.get` and
:func:`~mwapi.session.session.Session.post` afterwards.

.. autoclass:: mwapi.session.Session
    :members:

    ..autodata:: mwapi.session.Session.is_authenticated
"""
import requests

from .errors import APIError, LoginError


class Session:
    """
    Constructs a new API session.

    :Parameters:
        host : `str`
            Host to which to connect to. Must include http:// or https:// and
            no trailing "/".
        api_path : `str`
            The path to "api.php" on the server -- must begin with "/".
        session : `requests.Session`
            (optional) a `requests` session object to use
    """

    def __init__(self, host, api_path="/w/api.php", session=None):
        self.host = host
        self.api_path = api_path
        self.api_url = host + api_path
        self.session = session or requests.Session()

    def _request(self, method, params=None, data=None, files=None):
        resp = self.session.request(method, self.api_url, params=params,
                                    data=data, files=files, stream=True)

        try:
            doc = resp.json()
        except ValueError:
            raise ValueError("Could not decode as JSON:\n{0}"
                             .format(resp.text[:350]))

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
            :class`~mwapi.errors.LoginError` : if authentication fails
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
        """
        self.post(action='logout')

    def get(self, query_continue=None, **params):
        """Makes an API request with the GET method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
            params :
                Keyword parameters to be sent in the query string.
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
