import logging

import asyncio
import aiohttp

from .errors import (APIError, ConnectionError, RequestError, TimeoutError,
                     TooManyRedirectsError)
from .util import _normalize_params

DEFAULT_USERAGENT = "mwapi (python) -- default user-agent"

logger = logging.getLogger(__name__)


class AsyncSession:
    """
    Constructs a new API asynchronous session.

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
            and raising an error (
            :class:`aiohttp.client_exceptions.ServerTimeoutError` or
            :class:`asyncio.exceptions.TimeoutError`).
            By default aiohttp uses a total 300 seconds (5min) timeout.
        session : `aiohttp.ClientSession`
            (optional) an `aiohttp` session object to use
    """

    def __init__(self, host, user_agent=None, formatversion=None,
                 api_path=None,
                 timeout=None, session=None, **session_params):
        self.host = str(host)
        self.formatversion = int(formatversion) \
            if formatversion is not None else None
        self.api_path = str(api_path or "/w/api.php")
        self.api_url = self.host + self.api_path
        self.timeout = float(timeout) \
            if timeout is not None else aiohttp.ClientTimeout(total=300)
        self.session = session or aiohttp.ClientSession()
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

    async def _request(self, method, params=None, auth=None):
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
            async with self.session.request(method=method, url=self.api_url,
                                            params=params, data=data,
                                            timeout=self.timeout,
                                            headers=self.headers,
                                            verify_ssl=True,
                                            auth=auth) as resp:

                doc = await resp.json()

                if 'error' in doc:
                    raise APIError.from_doc(doc['error'])

                if 'warnings' in doc:
                    logger.warning("The following query raised warnings: {0}"
                                   .format(params or data))
                    for module, warning in doc['warnings'].items():
                        logger.warning("\t- {0} -- {1}"
                                       .format(module, warning))
                return doc

        except (ValueError, aiohttp.ContentTypeError):
            if resp is None:
                prefix = "No response data"
            else:
                prefix = (await resp.text())[:350]
            raise ValueError("Could not decode as JSON:\n{0}"
                             .format(prefix))
        except (aiohttp.ServerTimeoutError,
                asyncio.exceptions.TimeoutError) as e:
            raise TimeoutError(str(e)) from e
        except aiohttp.ClientConnectionError as e:
            raise ConnectionError(str(e)) from e
        except aiohttp.TooManyRedirects as e:
            raise TooManyRedirectsError(str(e)) from e
        except Exception as e:
            raise RequestError(str(e)) from e


    async def request(self, method, params=None, query_continue=None,
                      auth=None, continuation=False):
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
            return self._continuation(method, params=normal_params, auth=auth)
        else:
            return await self._request(method, params=normal_params, auth=auth)

    async def _continuation(self, method, params=None, auth=None):
        if "continue" not in params:
            params["continue"] = ""

        while True:
            doc = await self._request(method, params=params, auth=auth)
            yield doc
            if "continue" not in doc:
                break
            # re-send all continue values in the next call
            params.update(doc["continue"])

    async def get(self, query_continue=None, auth=None, continuation=False,
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
        return await self.request("GET", params=params, auth=auth,
                                  query_continue=query_continue,
                                  continuation=continuation)

    async def post(self, query_continue=None, auth=None, continuation=False,
                   **params):
        """Makes an API request with the POST method

        :Parameters:
            query_continue : `dict`
                Optionally, the value of a query continuation 'continue' field.
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
        return await self.request("POST", params=params, auth=auth,
                                  query_continue=query_continue,
                                  continuation=continuation)
