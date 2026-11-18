"""Brotli compression middleware for Django."""

import os
import re
from collections.abc import Iterable, Iterator
from typing import Final

import brotli
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    StreamingHttpResponse,
)
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin

RE_ACCEPT_ENCODING_BROTLI: Final = re.compile(r"\bbr\b")
_ETAG_CLOSING_QUOTE_RE: Final = re.compile(r'"$')
MIN_LEN_FOR_RESPONSE_TO_PROCESS: Final = 200
BROTLI_MODE: Final[int] = getattr(brotli, os.environ.get("BROTLI_MODE", "MODE_GENERIC"))
BROTLI_QUALITY: Final = int(os.environ.get("BROTLI_QUALITY", "4"))

__all__ = [
    "BROTLI_MODE",
    "BROTLI_QUALITY",
    "MIN_LEN_FOR_RESPONSE_TO_PROCESS",
    "RE_ACCEPT_ENCODING_BROTLI",
    "BrotliMiddleware",
    "compress",
]


def compress(content: bytes) -> bytes:
    """Compress the whole content at once."""
    compressed: bytes = brotli.compress(
        content, mode=BROTLI_MODE, quality=BROTLI_QUALITY
    )

    return compressed


class BrotliMiddleware(MiddlewareMixin):
    """Compress responses with brotli when the client accepts it.

    Based on Django's `GZipMiddleware`.
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponseBase
    ) -> HttpResponseBase:
        # Other HttpResponseBase subclasses have no known content attribute.
        if response.has_header("Content-Encoding") or not isinstance(
            response, HttpResponse | StreamingHttpResponse
        ):
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
            # TODO: async streaming responses stay uncompressed; add an async
            # compressor when someone needs it.
            if not isinstance(streaming_content, Iterable):
                return response

            response.streaming_content = self.compress_stream(streaming_content)
            # The compressed size is unknown until the stream ends.
            del response.headers["Content-Length"]
        else:
            compressed_content = compress(response.content)
            if len(compressed_content) >= len(response.content):
                return response

            response.content = compressed_content
            response.headers["Content-Length"] = str(len(compressed_content))

        if response.has_header("ETag"):
            response.headers["ETag"] = _ETAG_CLOSING_QUOTE_RE.sub(
                ';br"', response.headers["ETag"]
            )

        response.headers["Content-Encoding"] = "br"

        return response

    def compress_stream(self, streaming_content: Iterable[bytes]) -> Iterator[bytes]:
        """Compress the whole stream into a single chunk."""
        yield compress(b"".join(streaming_content))
