# -*- encoding: utf-8 -*-
# ! python3

import os
import re

import brotli
from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_vary_headers

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

RE_ACCEPT_ENCODING_BROTLI = re.compile(r"\bbr\b")
MIN_LEN_FOR_RESPONSE_TO_PROCESS = 200
BROTLI_MODE = getattr(brotli, os.environ.get("BROTLI_MODE", "MODE_GENERIC"))
BROTLI_QUALITY = int(os.environ.get("BROTLI_QUALITY", 4))

__all__ = [
    "BROTLI_MODE",
    "BROTLI_QUALITY",
    "MIN_LEN_FOR_RESPONSE_TO_PROCESS",
    "RE_ACCEPT_ENCODING_BROTLI",
    "BrotliMiddleware",
    "compress",
]


def compress(obj: bytes) -> bytes:
    return brotli.compress(obj, BROTLI_MODE, BROTLI_QUALITY)


# noinspection PyClassHasNoInit
class BrotliMiddleware(MiddlewareMixin):
    """
    This middleware compresses content if the browser allows `brotli` compression.
    It sets the Vary header accordingly, so that caches will base their storage
    on the Accept-Encoding header. Code of this middleware is based
    on Django's `GZipMiddleware`.
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if (
            response.has_header("Content-Encoding")
            or not self._accepts_brotli_encoding(request)
            or (
                not response.streaming
                and len(response.content) < MIN_LEN_FOR_RESPONSE_TO_PROCESS
            )
        ):
            # ---------
            # 1) brotlipy doesn't support streaming compression,
            #       see: https://github.com/google/brotli/issues/191
            # 2) Avoid brotli if we've already got a content-encoding.
            # 3) Client doesn't support brotli
            # 4) It's not worth attempting to compress really short responses.
            #    This was taken from django GZipMiddleware.
            # ---------
            return response

        patch_vary_headers(response, ("Accept-Encoding",))

        if response.streaming:
            compressed_content = self.compress_stream(response.streaming_content)
            response.streaming_content = compressed_content

            # Delete the `Content-Length` header for streaming content, because
            # we won't know the compressed size until we stream it.
            del response["Content-Length"]
        else:
            compressed_content = compress(response.content)

            # Return the compressed content only if it's actually shorter.
            if len(compressed_content) >= len(response.content):
                return response

            response.content = compressed_content
            response["Content-Length"] = str(len(compressed_content))

        if response.has_header("ETag"):
            response["ETag"] = re.sub(r"\"$", r";br\"", response["ETag"])

        response["Content-Encoding"] = "br"

        return response

    def compress_stream(self, streaming_content):
        streaming_content = [line.decode("utf-8") for line in list(streaming_content)]
        streaming_content = "".join(streaming_content).encode()
        streaming_content = (x for x in [compress(streaming_content)])

        return streaming_content

    # noinspection PyMethodMayBeStatic
    def _accepts_brotli_encoding(self, request: HttpRequest) -> bool:
        return bool(
            RE_ACCEPT_ENCODING_BROTLI.search(
                request.META.get("HTTP_ACCEPT_ENCODING", "")
            )
        )
