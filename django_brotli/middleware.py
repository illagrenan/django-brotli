"""Brotli compression middleware for Django."""

import os
import re
from collections.abc import AsyncIterable, AsyncIterator, Iterable, Iterator
from typing import Final

import brotli
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin

RE_ACCEPT_ENCODING_BROTLI: Final = re.compile(r"\bbr\b")
MIN_LEN_FOR_RESPONSE_TO_PROCESS: Final = 200
BROTLI_MODE: Final[int] = getattr(brotli, os.environ.get("BROTLI_MODE", "MODE_GENERIC"))
BROTLI_QUALITY: Final = int(os.environ.get("BROTLI_QUALITY", "4"))

__all__ = [
    "BROTLI_MODE",
    "BROTLI_QUALITY",
    "MIN_LEN_FOR_RESPONSE_TO_PROCESS",
    "RE_ACCEPT_ENCODING_BROTLI",
    "BrotliMiddleware",
    "acompress_stream",
    "compress",
    "compress_stream",
]


def compress(content: bytes) -> bytes:
    """Compress the whole content at once."""
    compressed: bytes = brotli.compress(
        content, mode=BROTLI_MODE, quality=BROTLI_QUALITY
    )

    return compressed


def compress_stream(chunks: Iterable[bytes]) -> Iterator[bytes]:
    """Compress chunks one by one, flushing each so the client gets it at once."""
    compressor = brotli.Compressor(mode=BROTLI_MODE, quality=BROTLI_QUALITY)
    for chunk in chunks:
        yield compressor.process(chunk) + compressor.flush()

    yield compressor.finish()


async def acompress_stream(chunks: AsyncIterable[bytes]) -> AsyncIterator[bytes]:
    """Async variant of `compress_stream`."""
    compressor = brotli.Compressor(mode=BROTLI_MODE, quality=BROTLI_QUALITY)
    async for chunk in chunks:
        yield compressor.process(chunk) + compressor.flush()

    yield compressor.finish()


class BrotliMiddleware(MiddlewareMixin):
    """Compress responses with brotli when the client accepts it.

    Mirrors Django's `GZipMiddleware`.
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponse | StreamingHttpResponse
    ) -> HttpResponse | StreamingHttpResponse:
        if response.has_header("Content-Encoding"):
            return response
        if (
            isinstance(response, HttpResponse)
            and len(response.content) < MIN_LEN_FOR_RESPONSE_TO_PROCESS
        ):
            return response

        patch_vary_headers(response, ("Accept-Encoding",))

        if not RE_ACCEPT_ENCODING_BROTLI.search(
            request.headers.get("Accept-Encoding", "")
        ):
            return response

        if isinstance(response, StreamingHttpResponse):
            streaming_content = response.streaming_content
            if isinstance(streaming_content, AsyncIterable):
                response.streaming_content = acompress_stream(streaming_content)
            else:
                response.streaming_content = compress_stream(streaming_content)
            # The compressed size is unknown until the stream ends.
            del response.headers["Content-Length"]
        else:
            compressed_content = compress(response.content)
            if len(compressed_content) >= len(response.content):
                return response

            response.content = compressed_content
            response.headers["Content-Length"] = str(len(compressed_content))

        # A strong ETag must change with the encoding; weaken it like GZipMiddleware.
        etag = response.headers.get("ETag")
        if etag and etag.startswith('"'):
            response.headers["ETag"] = f"W/{etag}"

        response.headers["Content-Encoding"] = "br"

        return response
