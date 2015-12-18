import mwapi
import mwoauth
from requests_oauthlib import OAuth1

# Consruct a "consumer" from the key/secret provided by MediaWiki
import config  # You'll need to provide this
from six.moves import input  # For compatibility between python 2 and 3

consumer_token = mwoauth.ConsumerToken(config.consumer_key,
                                       config.consumer_secret)

# Construct handshaker with wiki URI and consumer
handshaker = mwoauth.Handshaker("https://en.wikipedia.org/w/index.php",
                                consumer_token)

# Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
redirect, request_token = handshaker.initiate()

# Step 2: Authorize -- send user to MediaWiki to confirm authorization
print("Point your browser to: %s" % redirect)  #
response_qs = input("Response query string: ")

# Step 3: Complete -- obtain authorized key/secret for "resource owner"
access_token = handshaker.complete(request_token, response_qs)

# Construct an auth object with the consumer and access tokens
auth1 = OAuth1(consumer_token.key,
               client_secret=consumer_token.secret,
               resource_owner_key=access_token.key,
               resource_owner_secret=access_token.secret)

# Construct an mwapi session.  Nothing special here.
session = mwapi.Session(
    host="https://en.wikipedia.org",
    user_agent="mwoauth demo script -- ahalfaker@wikimedia.org")

# Now, accessing the API on behalf of a user
print("Reading top 10 watchlist items")
response = session.get(
    action="query",
    list="watchlist",
    wllimit=10,
    wlprop="title|comment",
    format="json",
    auth=auth1
)
for item in response.json()['query']['watchlist']:
    print("{title}\t{comment}".format(**item))
