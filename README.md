# Django Brotli: *Middleware that compresses response using brotli algorithm*

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![pypi](https://img.shields.io/badge/code%20style-The%20Ruff%20Formatter-000000.svg)](https://docs.astral.sh/ruff/formatter/)
[![pypi](https://img.shields.io/pypi/v/django-brotli.svg)](https://pypi.org/project/django-brotli/)
[![Python version](https://img.shields.io/pypi/pyversions/django-brotli.svg?logo=python&logoColor=white&label=python)](https://pypi.org/project/django-brotli/)
![Supported Django](https://img.shields.io/badge/django%20versions-%5E4.2%20||%20%5E5.0.3-blue.svg?logo=django&logoColor=white)
<br>
[![Build Status](https://github.com/illagrenan/django-brotli/actions/workflows/development.yml/badge.svg)](https://github.com/illagrenan/django-brotli/actions/workflows/development.yml)
[![codecov](https://codecov.io/gh/illagrenan/django-brotli/branch/main/graphs/badge.svg)](https://codecov.io/github/illagrenan/django-brotli)

* Documentation: <https://illagrenan.github.io/django-brotli>
* PyPI: <https://pypi.org/project/django-brotli/>
* License: [MIT](https://choosealicense.com/licenses/mit/)

## Introduction

This project consists of `BrotliMiddleware` which works the same as Django `GZipMiddleware` ([Docs](https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.gzip)/[Source](https://github.com/django/django/blob/master/django/middleware/gzip.py#L10-L52)). `BrotliMiddleware` will compress content of HTTP response using brotli algorithm (Brotli Compressed Data Format is defined in [RFC 7932](https://www.ietf.org/rfc/rfc7932.txt)).

In November 2016 is brotli supported by Firefox, Chrome, Android Browser and Opera (detailed stats on [caniuse](http://caniuse.com/#search=brotli)). Brotli is applied only when client has sent `Accept-Encoding` header containing `br`.

## Installation

**This software is in alpha version and should not be used in production.**

- Supported Python versions are: `">=3.10, <3.14"`.
- Supported Django versions are: `>=4,<6`.

```shell
pip install --upgrade django-brotli
```

Add `django_brotli.middleware.BrotliMiddleware` to `MIDDLEWARE`:

```python
MIDDLEWARE = [
    'django_brotli.middleware.BrotliMiddleware',
    # ...
]
```

## Credits and Resources

- [Brotli on Wikipedia](https://en.wikipedia.org/wiki/Brotli)
- [Brotli compression format repository by Google](https://github.com/google/brotli)

## Contributing

1. Clone this repository (`git clone ...`)
2. Create virtualenv
3. Install package dependencies: `pip install --upgrade -r requirements.txt`
4. Change some code
5. Run tests: in project root simply execute `pytest`
6. Submit PR :)

## License

The MIT License (MIT)

Copyright (c) 2016—2024 Václav Dohnal (@illagrenan)
