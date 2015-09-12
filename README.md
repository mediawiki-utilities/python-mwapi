# MediaWiki API

This MIT Licensed library provides a very simple convenience wrapper 
around the [MediaWiki API](http://www.mediawiki.org/wiki/API). and 
includes support for authenticated sessions. It requires Python 3
and that your wiki is using MediaWiki 1.15.3 or greater.

* **Installation:** ``pip install mwapi``
* **Documentation:** https://pythonhosted.org/mwapi
* **Repositiory:** https://github.com/mediawiki-utilities/python-mwapi
* **License:** MIT

## Example

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


## Authors
* YuviPanda -- https://github.com/yuvipanda
* Aaron Halfaker -- https://github.com/halfak
