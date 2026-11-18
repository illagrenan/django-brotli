# Django Brotli: *Middleware that compresses response using brotli algorithm*

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![pypi](https://img.shields.io/badge/code%20style-The%20Ruff%20Formatter-000000.svg)](https://docs.astral.sh/ruff/formatter/)
[![pypi](https://img.shields.io/pypi/v/django-brotli.svg)](https://pypi.org/project/django-brotli/)
[![Python version](https://img.shields.io/pypi/pyversions/django-brotli.svg?logo=python&logoColor=white&label=python)](https://pypi.org/project/django-brotli/)
![Supported Django](https://img.shields.io/badge/django%20versions-%5E5.2%20||%20%5E6.0-blue.svg?logo=django&logoColor=white)
<br>
[![Build Status](https://github.com/illagrenan/django-brotli/actions/workflows/development.yml/badge.svg)](https://github.com/illagrenan/django-brotli/actions/workflows/development.yml)
[![codecov](https://codecov.io/gh/illagrenan/django-brotli/branch/main/graphs/badge.svg)](https://codecov.io/github/illagrenan/django-brotli)

* PyPI: <https://pypi.org/project/django-brotli/>
* License: [MIT](https://choosealicense.com/licenses/mit/)

## Introduction

This project consists of `BrotliMiddleware` which works the same as Django `GZipMiddleware` ([Docs](https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.gzip)/[Source](https://github.com/django/django/blob/master/django/middleware/gzip.py#L10-L52)). `BrotliMiddleware` will compress content of HTTP response using brotli algorithm (Brotli Compressed Data Format is defined in [RFC 7932](https://www.ietf.org/rfc/rfc7932.txt)).

In November 2016 is brotli supported by Firefox, Chrome, Android Browser and Opera (detailed stats on [caniuse](http://caniuse.com/#search=brotli)). Brotli is applied only when client has sent `Accept-Encoding` header containing `br`.

## Installation

- Supported Python versions are: `>=3.11`.
- Supported Django versions are: `>=5.2`.

```console
uv add django-brotli
```

*or*

```console
pip install --upgrade django-brotli
```

Add `django_brotli.middleware.BrotliMiddleware` to `MIDDLEWARE`:

```python
MIDDLEWARE = [
    "django_brotli.middleware.BrotliMiddleware",
    # ...
]
```

## Configuration

Set these environment variables before Django starts; they are read once on import.

| Variable         | Default        | Values                                    |
|------------------|----------------|-------------------------------------------|
| `BROTLI_QUALITY` | `4`            | `0` (fastest) to `11` (smallest output)   |
| `BROTLI_MODE`    | `MODE_GENERIC` | `MODE_GENERIC`, `MODE_TEXT`, `MODE_FONT`  |

The default quality `4` is about 2× faster than Django's `GZipMiddleware` and gives about 20% smaller output ([#117](https://github.com/illagrenan/django-brotli/pull/117)).

## Credits and Resources

- [Brotli on Wikipedia](https://en.wikipedia.org/wiki/Brotli)
- [Brotli compression format repository by Google](https://github.com/google/brotli)

## Contributing

1. Clone this repository (`git clone ...`)
2. Install package dependencies: `uv sync`
3. Change some code
4. Run linters and tests: `uv run task lint coverage`
5. Submit PR :)

## License

[The MIT License (MIT)](./LICENSE)
