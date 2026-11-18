from django.conf import settings


def pytest_configure() -> None:
    settings.configure(
        DEBUG=False,
        INSTALLED_APPS=["django_brotli"],
        MIDDLEWARE=["django_brotli.middleware.BrotliMiddleware"],
        SECRET_KEY="not-a-real-key",  # noqa: S106 - test-only key
        ALLOWED_HOSTS=["*"],
    )
