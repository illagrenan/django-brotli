from collections.abc import AsyncIterator, Callable

import pytest
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from faker import Faker

from django_brotli.middleware import BrotliMiddleware


def pytest_configure() -> None:
    settings.configure(
        DEBUG=False,
        INSTALLED_APPS=["django_brotli"],
        MIDDLEWARE=["django_brotli.middleware.BrotliMiddleware"],
        SECRET_KEY="not-a-real-key",  # noqa: S106 - test-only key
        ALLOWED_HOSTS=["*"],
    )


@pytest.fixture(scope="session")
def faker() -> Faker:
    """Faker shared by all tests."""
    return Faker()


@pytest.fixture
def sample_text(faker: Faker) -> str:
    """Text long enough to be compressed."""
    return " ".join(faker.paragraphs(nb=20))


@pytest.fixture
def short_text() -> str:
    """Text too short to be compressed."""
    return "Too short to compress."


@pytest.fixture
def streaming_chunks(faker: Faker) -> list[bytes]:
    """Text chunks of a streaming response."""
    return [faker.paragraph(nb_sentences=50).encode() for _ in range(3)]


@pytest.fixture
def async_chunks_factory() -> Callable[[list[bytes]], AsyncIterator[bytes]]:
    """Factory turning chunks into an async iterator."""

    async def _factory(chunks: list[bytes]) -> AsyncIterator[bytes]:
        for chunk in chunks:
            yield chunk

    return _factory


@pytest.fixture
def brotli_request() -> HttpRequest:
    """Request from a client that accepts brotli."""
    return RequestFactory().get("/", headers={"Accept-Encoding": "gzip, deflate, br"})


@pytest.fixture
def legacy_request() -> HttpRequest:
    """Request from a client without brotli support."""
    return RequestFactory().get("/", headers={"Accept-Encoding": "gzip, deflate"})


@pytest.fixture
def brotli_middleware() -> BrotliMiddleware:
    """Middleware with a dummy get_response."""
    return BrotliMiddleware(get_response=lambda request: HttpResponse())
