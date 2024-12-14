# -*- encoding: utf-8 -*-
# ! python3

from django.conf import settings


def pytest_configure():
    settings.configure(
        DEBUG=False,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_brotli",
        ],
        MIDDLEWARE=[
            "django_brotli.middleware.BrotliMiddleware",
        ],
        SECRET_KEY="not-a-real-key",  # noqa: S106
        ALLOWED_HOSTS=["*"],
    )
