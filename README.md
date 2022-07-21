# MediaWiki API

This MIT-licensed library provides a very simple convenience wrapper 
around the [MediaWiki API](https://www.mediawiki.org/wiki/API), 
including support for authenticated sessions. It requires Python 3
and that your wiki is using MediaWiki 1.15.3 or greater.

* **Installation:** ``pip install mwapi``
* **Documentation:** https://pythonhosted.org/mwapi
* **Repository:** https://github.com/mediawiki-utilities/python-mwapi
* **License:** MIT

## Examples

### Single query

    >>> import mwapi
    >>>
    >>> session = mwapi.Session('https://en.wikipedia.org')
    >>>
    >>> print(session.get(action='query', meta='userinfo'))
    {'query': {'userinfo': {'anon': '', 'name': '75.72.203.28', 'id': 0}},
     'batchcomplete': ''}
    >>>
    >>> print(session.get(action='query', prop='revisions', revids=32423425))
    {'query': {'pages': {'1429626': {'ns': 0, 'revisions': [{'user':
     'Wknight94', 'parentid': 32276615, 'comment':
     '/* References */ Removing less-specific cat', 'revid': 32423425,
     'timestamp': '2005-12-23T00:07:17Z'}], 'title': 'Grigol Ordzhonikidze',
     'pageid': 1429626}}}, 'batchcomplete': ''}

### Query with continuation

```python
import mwapi
from mwapi.errors import APIError

session = mwapi.Session('https://en.wikipedia.org/')

# If passed a `continuation` parameter, returns an iterable over a continued query.
# On each iteration, a new request is made for the next portion of the results.
continued = session.get(
    formatversion=2,
    action='query',
    generator='categorymembers',
    gcmtitle='Category:17th-century classical composers',
    gcmlimit=100,  # 100 results per request
    continuation=True)

pages = []
try:
    for portion in continued:
        if 'query' in portion:
            for page in portion['query']['pages']:
                pages.append(page['title'])
        else:
            print("MediaWiki returned empty result batch.")
except APIError as error:
    raise ValueError(
        "MediaWiki returned an error:", str(error)
    )

print("Fetched {} pages".format(len(pages)))
```

### Asynchronous single query

```python
import asyncio
import aiohttp
import mwapi

async def query():
    async with aiohttp.ClientSession() as s:
        session = mwapi.AsyncSession(
                    'https://en.wikipedia.org',
                    user_agent='mwapi async demo',
                    session=s)
        response = await asyncio.create_task(
            session.get(action='query', prop='revisions', revids=32423425)
        )
    print(response)

asyncio.run(query())
```    

### Asynchronous query with continuation

```python
import asyncio
import aiohttp

import mwapi
from mwapi.errors import APIError

async def query():
    async with aiohttp.ClientSession() as s:
        session = mwapi.AsyncSession(
                    'https://en.wikipedia.org',
                    user_agent='mwapi async demo',
                    session=s)

        continued = await asyncio.create_task(
            session.get(
                formatversion=2,
                action='query',
                generator='categorymembers',
                gcmtitle='Category:17th-century classical composers',
                gcmlimit=100,  # 100 results per request
                continuation=True)
        )
        pages = []
        try:
            async for portion in continued:
                if 'query' in portion:
                    for page in portion['query']['pages']:
                        pages.append(page['title'])
                else:
                    print("MediaWiki returned empty result batch.")
        except APIError as error:
            raise ValueError(
                "MediaWiki returned an error:", str(error)
            )
    print("Fetched {} pages".format(len(pages)))

asyncio.run(query())
```

## Authors
* YuviPanda -- https://github.com/yuvipanda
* Aaron Halfaker -- https://github.com/halfak
