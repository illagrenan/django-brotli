# -*- encoding: utf-8 -*-
# ! python3

import gzip
from typing import MutableMapping, Optional
from unittest import TestCase

import brotli
from django.http import StreamingHttpResponse
from django.middleware.gzip import GZipMiddleware

from django_brotli.middleware import BrotliMiddleware, MIN_LEN_FOR_RESPONSE_TO_PROCESS
from .utils import UTF8_LOREM_IPSUM_IN_CZECH


class FakeRequestAcceptsBrotli:
    META = {"HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch, br"}


class FakeLegacyRequest:
    META = {"HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch"}


class FakeResponse:
    streaming = False

    def __init__(
        self,
        content: str,
        headers: Optional[MutableMapping[str, str]] = None,
        streaming: Optional[bool] = None,
    ):
        self.content = content.encode(encoding="utf-8")
        self.headers = headers or {}

        if streaming:
            self.streaming = streaming

    def has_header(self, header: str) -> bool:
        return header in self.headers

    def get(self, key):
        return self.headers.get(key, None)

    def __getitem__(self, header: str) -> str:
        return self.headers[header]

    def __setitem__(self, header: str, value: str):
        self.headers[header] = value


class MiddlewareTestCase(TestCase):
    def test_middleware_compress_response(self):
        fake_request = FakeRequestAcceptsBrotli()
        response_content = UTF8_LOREM_IPSUM_IN_CZECH
        fake_response = FakeResponse(content=response_content)

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(
            fake_request, fake_response
        )

        decompressed_response = brotli.decompress(brotli_response.content)  # type: bytes
        self.assertEqual(
            response_content, decompressed_response.decode(encoding="utf-8")
        )

    def test_compress_streaming_response(self):
        """
        Compression is performed on responses with streaming content.
        """
        sequence = [b"a" * 500, b"b" * 200, b"a" * 300]

        def get_stream_response():
            resp = StreamingHttpResponse(sequence)
            resp["Content-Type"] = "text/html; charset=UTF-8"
            return resp

        fake_request = FakeRequestAcceptsBrotli()
        fake_response = get_stream_response()

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(
            fake_request, fake_response
        )

        decompressed_response = brotli.decompress(
            b"".join(brotli_response.streaming_content)
        )  # type: bytes

        self.assertEqual(b"".join(sequence), decompressed_response)
        self.assertEqual(brotli_response.get("Content-Encoding"), "br")
        self.assertFalse(brotli_response.has_header("Content-Length"))

    def test_etag_is_updated_if_present(self):
        fake_request = FakeRequestAcceptsBrotli()
        response_content = UTF8_LOREM_IPSUM_IN_CZECH * 5
        fake_etag_content = '"foo"'
        fake_response = FakeResponse(
            content=response_content, headers={"ETag": fake_etag_content}
        )

        self.assertEqual(fake_response["ETag"], fake_etag_content)

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(
            fake_request, fake_response
        )

        decompressed_response = brotli.decompress(brotli_response.content)  # type: bytes
        self.assertEqual(
            response_content, decompressed_response.decode(encoding="utf-8")
        )

        self.assertEqual(brotli_response["ETag"], '"foo;br\\"')

    def test_middleware_wont_compress_response_if_response_is_small(self):
        fake_request = FakeRequestAcceptsBrotli()
        response_content = "Hello World"

        self.assertLess(len(response_content), MIN_LEN_FOR_RESPONSE_TO_PROCESS)  # a < b

        fake_response = FakeResponse(content=response_content)

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(
            fake_request, fake_response
        )

        self.assertEqual(
            response_content, brotli_response.content.decode(encoding="utf-8")
        )

    def test_middleware_wont_compress_if_client_not_accept(self):
        fake_request = FakeLegacyRequest()
        response_content = UTF8_LOREM_IPSUM_IN_CZECH
        fake_response = FakeResponse(content=response_content)

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(
            fake_request, fake_response
        )

        self.assertEqual(
            response_content, brotli_response.content.decode(encoding="utf-8")
        )

    def test_middleware_wont_compress_if_response_is_already_compressed(self):
        fake_request = FakeRequestAcceptsBrotli()
        response_content = UTF8_LOREM_IPSUM_IN_CZECH
        fake_response = FakeResponse(content=response_content)

        brotli_middleware = BrotliMiddleware()
        django_gzip_middleware = GZipMiddleware()

        gzip_response = django_gzip_middleware.process_response(
            fake_request, fake_response
        )
        brotli_response = brotli_middleware.process_response(
            fake_request, gzip_response
        )

        self.assertEqual(
            response_content,
            gzip.decompress(brotli_response.content).decode(encoding="utf-8"),
        )
