import gzip
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

import brotli
import pytest
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    StreamingHttpResponse,
)
from django.middleware.gzip import GZipMiddleware

from django_brotli.middleware import BrotliMiddleware


def test_response_is_compressed(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request, response=HttpResponse(content=sample_text)
    )
    assert isinstance(response, HttpResponse)

    assert brotli.decompress(response.content).decode() == sample_text
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Encoding": "br",
        "Content-Length": str(len(response.content)),
        "Vary": "Accept-Encoding",
    }


def test_streaming_response_is_compressed(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    streaming_chunks: list[bytes],
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request,
        response=StreamingHttpResponse(streaming_content=streaming_chunks),
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, Iterator)

    compressed = b"".join(response.streaming_content)

    assert brotli.decompress(compressed) == b"".join(streaming_chunks)
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Encoding": "br",
        "Vary": "Accept-Encoding",
    }


def test_binary_streaming_response_is_compressed(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    binary_chunks: list[bytes],
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request,
        response=StreamingHttpResponse(streaming_content=binary_chunks),
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, Iterator)

    compressed = b"".join(response.streaming_content)

    assert brotli.decompress(compressed) == b"".join(binary_chunks)


@pytest.mark.asyncio
async def test_async_streaming_response_is_passed_through(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    streaming_chunks: list[bytes],
    async_chunks_factory: Callable[[list[bytes]], AsyncIterator[bytes]],
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request,
        response=StreamingHttpResponse(
            streaming_content=async_chunks_factory(streaming_chunks)
        ),
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, AsyncIterator)

    content = b"".join([chunk async for chunk in response.streaming_content])

    assert content == b"".join(streaming_chunks)
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Vary": "Accept-Encoding",
    }


def test_etag_gets_brotli_suffix(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    original_response = HttpResponse(content=sample_text, headers={"ETag": '"foo"'})

    response = brotli_middleware.process_response(
        request=brotli_request, response=original_response
    )

    assert response["ETag"] == '"foo;br"'


def test_short_response_is_not_compressed(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, short_text: str
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request, response=HttpResponse(content=short_text)
    )
    assert isinstance(response, HttpResponse)

    assert response.content.decode() == short_text
    assert dict(response.headers) == {"Content-Type": "text/html; charset=utf-8"}


def test_incompressible_response_is_not_compressed(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    incompressible_content: bytes,
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request, response=HttpResponse(content=incompressible_content)
    )
    assert isinstance(response, HttpResponse)

    assert response.content == incompressible_content
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Vary": "Accept-Encoding",
    }


def test_unknown_response_type_is_passed_through(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    bare_response: HttpResponseBase,
) -> None:
    response = brotli_middleware.process_response(
        request=brotli_request, response=bare_response
    )

    assert response is bare_response
    assert dict(response.headers) == {"Content-Type": "text/html; charset=utf-8"}


def test_response_is_not_compressed_for_client_without_brotli(
    legacy_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    response = brotli_middleware.process_response(
        request=legacy_request, response=HttpResponse(content=sample_text)
    )
    assert isinstance(response, HttpResponse)

    assert response.content.decode() == sample_text
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Vary": "Accept-Encoding",
    }


def test_gzipped_response_is_not_compressed_again(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    gzip_middleware: GZipMiddleware,
    sample_text: str,
) -> None:
    gzip_response = gzip_middleware.process_response(
        request=brotli_request, response=HttpResponse(content=sample_text)
    )
    assert isinstance(gzip_response, HttpResponse)

    response = brotli_middleware.process_response(
        request=brotli_request, response=gzip_response
    )
    assert isinstance(response, HttpResponse)

    assert gzip.decompress(response.content).decode() == sample_text
    assert response["Content-Encoding"] == "gzip"


@pytest.mark.parametrize(
    "content_encoding",
    argvalues=[
        pytest.param("gzip", id="gzip"),
        pytest.param("br", id="brotli"),
        pytest.param("deflate", id="deflate"),
        pytest.param("compress", id="compress"),
    ],
)
def test_already_encoded_response_is_skipped(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
    content_encoding: str,
) -> None:
    original_response = HttpResponse(
        content=sample_text, headers={"Content-Encoding": content_encoding}
    )

    response = brotli_middleware.process_response(
        request=brotli_request, response=original_response
    )
    assert isinstance(response, HttpResponse)

    assert response.content.decode() == sample_text
    assert dict(response.headers) == {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Encoding": content_encoding,
    }


def test_middleware_compresses_view_response(
    brotli_request: HttpRequest,
    middleware_factory: Callable[[HttpResponse], BrotliMiddleware],
    sample_text: str,
) -> None:
    middleware = middleware_factory(HttpResponse(content=sample_text))

    response = middleware(brotli_request)
    assert isinstance(response, HttpResponse)

    assert brotli.decompress(response.content).decode() == sample_text
    assert response["Content-Encoding"] == "br"


@pytest.mark.asyncio
async def test_async_middleware_compresses_view_response(
    brotli_request: HttpRequest,
    async_middleware_factory: Callable[[HttpResponse], BrotliMiddleware],
    sample_text: str,
) -> None:
    middleware = async_middleware_factory(HttpResponse(content=sample_text))

    pending_response = middleware(brotli_request)
    assert isinstance(pending_response, Awaitable)
    response = await pending_response
    assert isinstance(response, HttpResponse)

    assert brotli.decompress(response.content).decode() == sample_text
    assert response["Content-Encoding"] == "br"
