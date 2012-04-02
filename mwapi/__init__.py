# Copyright (c) 2012 Yuvi Panda <yuvipanda@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
try: import simplejson as json
except ImportError: import json

class MWApi:
    """
    Class representing a single API Session, with a single authenticated user.

    Useful Attributes:
    tokens              - Contains an edittoken & watchtoken (if populateTokens() has been called)
    is_authenticated    - Boolean indicating if the MWApi is sending authenticated requests
    """

    # Default for all API requests
    DEFAULT_PARAMS = {
            "format": "json"
    }

    def __init__(self, host, api_path="/w/api.php"):
        """Create a MWApi instance
        
        Arguments:
        host        - Host to which to connect to. Must include http:// or https:// and no trailing slash
        api_path    - Url to api.php on the host. Must start with /
        """
        self.host = host
        self.api_path = api_path
        self.api_url = host + api_path
        self.session = requests.session(params=MWApi.DEFAULT_PARAMS)
        self.tokens = {}
        self.is_authenticated = False
    
    def request(self, method, params):
        """Makes a request to the API and returns a dictionary containing the results

        Arguments:
        method - GET or POST, depending on which API is being called
        params - Parameters to send to the API. Varies depending on the action to be performed. 
        """
        resp = self.session.request(
                method, 
                self.api_url,
                params=params,
                prefetch=True)
        return json.loads(resp.content)

    def login(self, username, password):
        """Authenticates with the given credentials and logs in the user for the session. 
        All further requests sent from this MWApi object will be signed as said user.

        Arguments:
        username - The username of the user to be authenticated
        password - The password of the user to be authenticated
        
        Throws:
        Throws an exception with (Message, Response) if Authentication fails

        Note: 
        Passwords are sent as plaintext. This is a limitation of the Mediawiki API.
        Use a https host if you want your password to be secure
        """
        login = self.post({
            "action": "login",
            "lgname": username,
            "lgpassword": password
        })

        confirm = self.post({
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login['login']['token']
        })

        result = confirm['login']['result']
        if result != 'Success':
            raise Exception("Login failed with result %s" % result, confirm)
        self.is_authenticated = True

    def populateTokens(self):
        """Populates the `tokens` attribute of the object with `edittoken` and `watchtoken`.
        Requires that authentication has been performed already with `login()`
        """
        info = self.get({
            "action": "query",
            "prop": "info",
            "titles": "Main_Page",
            "intoken": 'edit|watch'
            })
        page = info["query"]["pages"].values()[0]
        self.tokens = {
                "edittoken": page["edittoken"],
                "watchtoken": page["watchtoken"]
                }


    def get(self, params):
        """Makes an API request with the GET method

        Arguments:
        params - Parameters to send to the API. Varies depending on the action to be performed. 
        """
        return self.request('GET', params)

    def post(self, params):
        """Makes an API request with the POST method

        Arguments:
        params - Parameters to send to the API. Varies depending on the action to be performed. 
        """
        return self.request('POST', params)

