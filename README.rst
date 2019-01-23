===========================================================================
Django Brotli: *Middleware that compresses response using brotli algorithm*
===========================================================================

.. image:: https://img.shields.io/pypi/v/django-brotli.svg
    :target: https://pypi.python.org/pypi/django-brotli
    :alt: PyPi

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://pypi.python.org/pypi/django-brotli/
    :alt: MIT

.. image:: https://img.shields.io/travis/illagrenan/django-brotli.svg
    :target: https://travis-ci.org/illagrenan/django-brotli
    :alt: TravisCI

.. image:: https://img.shields.io/coveralls/illagrenan/django-brotli.svg
    :target: https://coveralls.io/github/illagrenan/django-brotli?branch=master
    :alt: Coverage

.. image:: https://pyup.io/repos/github/illagrenan/django-brotli/shield.svg
    :target: https://pyup.io/repos/github/illagrenan/django-brotli/
    :alt: Updates

.. image:: https://img.shields.io/pypi/implementation/django-brotli.svg
    :target: https://pypi.python.org/pypi/django_brotli/
    :alt: Supported Python implementations

.. image:: https://img.shields.io/pypi/pyversions/django-brotli.svg
    :target: https://pypi.python.org/pypi/django_brotli/
    :alt: Supported Python versions

Introduction
------------

This project consists of ``BrotliMiddleware`` which works the same as Django ``GZipMiddleware`` (`Docs`_/`Source`_). ``BrotliMiddleware`` will compress content of HTTP response using brotli algorithm (Brotli Compressed Data Format is defined in `RFC 7932`_).

In November 2016 is brotli supported by Firefox, Chrome, Android Browser and Opera (detailed stats on `caniuse`_). Brotli is applied only when client has sent ``Accept-Encoding`` header containing ``br``.

.. _`Docs`: https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.gzip
.. _`Source`: https://github.com/django/django/blob/master/django/middleware/gzip.py#L10-L52
.. _`RFC 7932`: https://www.ietf.org/rfc/rfc7932.txt
.. _`caniuse`: http://caniuse.com/#search=brotli

Installation
------------

**This software is in alpha version and should not be used in production.**

- Supported Python versions are: ``3.5``, ``3.6`` and ``3.7``.
- Supported Django versions are: ``1.11.x`` (LTS), ``2.0.x`` and ``2.1.x`` (LTS).

.. code:: shell

    pip install --upgrade django-brotli


Add ``django_brotli.middleware.BrotliMiddleware`` to ``MIDDLEWARE``:

.. code:: python

    MIDDLEWARE = [
        'django_brotli.middleware.BrotliMiddleware',
        # ...
    ]


Credits and Resources
---------------------

- `Brotli on Wikipedia (https://en.wikipedia.org/wiki/Brotli) <https://en.wikipedia.org/wiki/Brotli>`_
- `Brotli compression format repository by Google (https://github.com/google/brotli) <https://github.com/google/brotli>`_


Contributing
------------

1. Clone this repository (``git clone ...``)
2. Create virtualenv
3. Install package dependencies: ``pip install --upgrade -r requirements.txt``
4. Change some code
5. Run tests: in project root simply execute ``pytest``
6. Submit PR :)

License
-------

The MIT License (MIT)

Copyright (c) 2016–2019 Vašek Dohnal (@illagrenan)
