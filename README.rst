============================================================================
Django Brotli: *Middleware that compresses response using brotli algorithm.*
============================================================================

.. image:: https://badge.fury.io/py/django-brotli.svg
        :target: https://pypi.python.org/pypi/django-brotli
        :alt: PyPi

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://pypi.python.org/pypi/django-brotli/
        :alt: MIT

.. image:: https://api.travis-ci.org/illagrenan/django-brotli.svg
        :target: https://travis-ci.org/illagrenan/django-brotli
        :alt: TravisCI

.. image:: https://coveralls.io/repos/github/illagrenan/django-brotli/badge.svg?branch=master
        :target: https://coveralls.io/github/illagrenan/django-brotli?branch=master
        :alt: Coverage

.. image:: https://pyup.io/repos/github/illagrenan/django-brotli/shield.svg
     :target: https://pyup.io/repos/github/illagrenan/django-brotli/
     :alt: Updates

.. image:: https://pyup.io/repos/github/illagrenan/django-brotli/python-3-shield.svg
     :target: https://pyup.io/repos/github/illagrenan/django-brotli/
     :alt: Python 3

Introduction
------------

TODO

Installation
------------

- Supported Python versions are: only ``3.5``.
- Supported Django versions are: only ``1.10.x``.

.. code:: shell

    pip install --upgrade django-brotli


Add ``django_brotli.middleware.BrotliMiddleware`` to ``MIDDLEWARE``:

.. code:: python

    MIDDLEWARE = [
        'django_brotli.middleware.BrotliMiddleware',
        # ...
    ]


Inspiration and Credits
-----------------------

TODO


License
-------

The MIT License (MIT)

Copyright (c) 2016 Vašek Dohnal (@illagrenan)

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
