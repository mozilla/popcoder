popcoder
========

|Travis|

Python library for transcoding popcorn code into flat video files

Installation
------------

::

    pip install popcoder


Development
-----------

To run the tests run:

::

    python setup.py test

Releases
--------

To make a new release, increment the version number in
``popcoder/__init__.py`` where the ``__version__`` variable is set.
Then push to master and wait for
`Travis CI <https://travis-ci.org/mozilla/popcoder>`__  to finish successfully
building. It will push a new release to
`PyPI <https://pypi.python.org/pypi/popcoder>`__. 


.. |Travis| image:: https://travis-ci.org/mozilla/popcoder.png?branch=master
   :target: https://travis-ci.org/mozilla/popcoder
