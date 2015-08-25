"""
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


class Session:
    """
    Constructs a new API session.

    :Parameters:
        host : `str`
            Host to which to connect to. Must include http:// or https:// and
            no trailing "/".
        api_path : `str
            The path to "api.php" on the server -- must begin with "/".
        session : `requests.Session`
            (optional) a `requests` session object to use
    """

    def __init__(self, host, api_path="/w/api.php", session=None):
        self.host = host
        self.api_path = api_path
        self.api_url = host + api_path
        self.session = session or requests.session()
        self.is_authenticated = False
        """
        `bool` : Is the session sending authenticated requests
        """

    def _request(self, method, params=None, data=None, files=None):
        resp = self.session.request(
                method,
                self.api_url,
                params=params,
                data=data,
                files=files,
                stream=True)
        return resp.json()

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
        login = self.post(action="login", lgname=username, lgpassword=password)

        confirm = self.post(action="login", lgname=username,
                            lgpassword=password, lgtoken=login['login']['token'])

        result = confirm['login']['result']
        if result != 'Success':
            raise Exception("Login failed with result %s" % result, confirm)
        self.is_authenticated = True
        return result

    def logout(self):
        """
        Logs out of the session with MediaWiki
        """
        self.post(action='logout')
        self.is_authenticated = False

    def get_auth_cookie(self):
        """
        Returns the user's authentication cookie
        """
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def set_auth_cookie(self, auth_cookie):
        """
        Updates the user's authentication cookie
        """
        self.session.cookies = requests.utils.cookiejar_from_dict(auth_cookie)

    def validate_login(self):
        """
        Updates and returns the user's logged-in status
        """
        data = self.get(action='query', meta='userinfo')
        self.is_authenticated = 'anon' not in data['query']['userinfo']
        return self.is_authenticated

    def get_tokens(self, tokens="edit"):
        """
        Gets a token

        """
        data = self.get(action="tokens", type=tokens)
        return data['tokens']


    def get(self, **kwparams):
        """Makes an API request with the GET method

        :Parameters:
            **kwparams : dict
                Keyword parameters to be sent in the query string.
        """
        kwparams['format'] = 'json'
        return self._request('GET', kwparams)

    def post(self, **kwparams):
        """Makes an API request with the POST method

        :Parameters:
            **kwparams : dict
                Keyword parameters to be sent in the POST message body.
        """
        kwparams['format'] = 'json'
        return self._request('POST', data=kwparams)

    def upload(self, file, **kwparams):
        """Uploads a file

        :Parameters:
            file : `bytes`
                Bytes representing the file to upload.
            **kwparams : dict
                Additional keyword parameters to be sent in the POST message
                body.
        """
        kwparams['format'] = 'json'
        files = {'file': file}
        return self._request('POST', data=kwparams, files=files)
