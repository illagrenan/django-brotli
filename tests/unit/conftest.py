import os
from collections.abc import AsyncIterator, Callable

import pytest
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.middleware.gzip import GZipMiddleware
from django.test import RequestFactory
from faker import Faker

from django_brotli.middleware import BrotliMiddleware


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
def binary_chunks() -> list[bytes]:
    """Chunks that are not valid UTF-8."""
    return [bytes(range(256)) * 4, b"\xff\xfe" * 300]


@pytest.fixture
def incompressible_content() -> bytes:
    """Random bytes that brotli cannot shrink."""
    return os.urandom(1_000)


@pytest.fixture
def bare_response() -> HttpResponseBase:
    """Response that is neither HttpResponse nor StreamingHttpResponse."""
    return HttpResponseBase()


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
    return RequestFactory().get(
        path="/", headers={"Accept-Encoding": "gzip, deflate, br"}
    )


@pytest.fixture
def legacy_request() -> HttpRequest:
    """Request from a client without brotli support."""
    return RequestFactory().get(path="/", headers={"Accept-Encoding": "gzip, deflate"})


@pytest.fixture
def brotli_middleware() -> BrotliMiddleware:
    """Middleware with a dummy get_response."""
    return BrotliMiddleware(get_response=lambda request: HttpResponse())


@pytest.fixture
def gzip_middleware() -> GZipMiddleware:
    """Django's gzip middleware with a dummy get_response."""
    return GZipMiddleware(get_response=lambda request: HttpResponse())


@pytest.fixture
def middleware_factory() -> Callable[[HttpResponse], BrotliMiddleware]:
    """Factory wrapping a sync view that returns the given response."""

    def _factory(response: HttpResponse) -> BrotliMiddleware:
        return BrotliMiddleware(get_response=lambda request: response)

    return _factory


@pytest.fixture
def async_middleware_factory() -> Callable[[HttpResponse], BrotliMiddleware]:
    """Factory wrapping an async view that returns the given response."""

    def _factory(response: HttpResponse) -> BrotliMiddleware:
        async def get_response(request: HttpRequest) -> HttpResponse:
            return response

        return BrotliMiddleware(get_response=get_response)

    return _factory
