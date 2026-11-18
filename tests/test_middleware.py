import gzip
from collections.abc import AsyncIterator, Callable, Iterator

import brotli
import pytest
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.middleware.gzip import GZipMiddleware

from django_brotli.middleware import BrotliMiddleware


def test_response_is_compressed(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    response = brotli_middleware.process_response(
        brotli_request, HttpResponse(sample_text)
    )

    assert brotli.decompress(response.content).decode() == sample_text
    assert response["Content-Encoding"] == "br"
    assert response["Content-Length"] == str(len(response.content))
    assert response["Vary"] == "Accept-Encoding"


def test_streaming_response_is_compressed_chunk_by_chunk(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    streaming_chunks: list[bytes],
) -> None:
    response = brotli_middleware.process_response(
        brotli_request, StreamingHttpResponse(streaming_chunks)
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, Iterator)

    compressed_chunks = list(response.streaming_content)

    assert brotli.decompress(b"".join(compressed_chunks)) == b"".join(streaming_chunks)
    assert len(compressed_chunks) == len(streaming_chunks) + 1
    assert response["Content-Encoding"] == "br"
    assert not response.has_header("Content-Length")


def test_binary_streaming_response_is_compressed(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware
) -> None:
    binary_chunks = [bytes(range(256)) * 4, b"\xff\xfe" * 300]

    response = brotli_middleware.process_response(
        brotli_request, StreamingHttpResponse(binary_chunks)
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, Iterator)

    assert brotli.decompress(b"".join(response.streaming_content)) == b"".join(
        binary_chunks
    )


async def test_async_streaming_response_is_compressed(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    streaming_chunks: list[bytes],
    async_chunks_factory: Callable[[list[bytes]], AsyncIterator[bytes]],
) -> None:
    response = brotli_middleware.process_response(
        brotli_request, StreamingHttpResponse(async_chunks_factory(streaming_chunks))
    )
    assert isinstance(response, StreamingHttpResponse)
    assert isinstance(response.streaming_content, AsyncIterator)

    compressed = b"".join([chunk async for chunk in response.streaming_content])

    assert brotli.decompress(compressed) == b"".join(streaming_chunks)
    assert response["Content-Encoding"] == "br"


def test_strong_etag_is_weakened(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    original_response = HttpResponse(sample_text, headers={"ETag": '"foo"'})

    response = brotli_middleware.process_response(brotli_request, original_response)

    assert response["ETag"] == 'W/"foo"'


def test_short_response_is_not_compressed(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, short_text: str
) -> None:
    response = brotli_middleware.process_response(
        brotli_request, HttpResponse(short_text)
    )

    assert response.content.decode() == short_text
    assert not response.has_header("Content-Encoding")


def test_response_is_not_compressed_for_client_without_brotli(
    legacy_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    response = brotli_middleware.process_response(
        legacy_request, HttpResponse(sample_text)
    )

    assert response.content.decode() == sample_text
    assert not response.has_header("Content-Encoding")
    assert response["Vary"] == "Accept-Encoding"


def test_gzipped_response_is_not_compressed_again(
    brotli_request: HttpRequest, brotli_middleware: BrotliMiddleware, sample_text: str
) -> None:
    gzip_middleware = GZipMiddleware(get_response=lambda request: HttpResponse())
    gzip_response = gzip_middleware.process_response(
        brotli_request, HttpResponse(sample_text)
    )
    assert isinstance(gzip_response, HttpResponse)

    response = brotli_middleware.process_response(brotli_request, gzip_response)

    assert gzip.decompress(response.content).decode() == sample_text


@pytest.mark.parametrize("content_encoding", ["gzip", "br", "deflate", "compress"])
def test_already_encoded_response_is_skipped(
    brotli_request: HttpRequest,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
    content_encoding: str,
) -> None:
    original_response = HttpResponse(
        sample_text, headers={"Content-Encoding": content_encoding}
    )

    response = brotli_middleware.process_response(brotli_request, original_response)

    assert response["Content-Encoding"] == content_encoding
    assert response.content.decode() == sample_text
