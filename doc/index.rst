MediaWiki API
=============

This library provides a set of basic utilities for interacting with MediaWiki's
"action" API -- usually available at /w/api.php.  The most salient feature of
this library is the :class:`~mwapi.session.Session` class that provides a
connection session that sustains a logged-in user status and provides
convenience functions for calling the MediaWiki API -- for example,
:func:`~mwapi.session.Session.get`, :func:`~mwapi.session.Session.post`, and
:func:`~mwapi.session.Session.login`.

Contents
--------
.. toctree::
    :maxdepth: 2

    session
    errors

Authors
-------
* YuviPanda -- https://github.com/yuvipanda
* Aaron Halfaker -- https://github.com/halfak

.. code::

  MIT LICENSE
  
  Copyright (c) 2012 Yuvi Panda <yuvipanda@gmail.com>

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation
  files (the "Software"), to deal in the Software without
  restriction, including without limitation the rights to use,
  copy, modify, merge, publish, distribute, sublicense, and/or
  sell copies of the Software, and to permit persons to whom
  the Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall
  be included in all copies or substantial portions of the
  Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
  OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
