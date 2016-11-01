# -*- encoding: utf-8 -*-
# ! python3

from typing import Mapping, Optional
from unittest import TestCase

import brotli

from django_brotli.middleware import BrotliMiddleware


class FakeRequest(object):
    META = {
        'HTTP_ACCEPT_ENCODING': 'gzip, deflate, sdch, br'
    }


class FakeResponse(object):
    streaming = False

    def __init__(self, content: str, headers: Optional[Mapping[str, str]] = None, streaming: Optional[bool] = None):
        self.content = content.encode(encoding='utf-8')
        self.headers = headers or {}

        if streaming:
            self.streaming = streaming

    def has_header(self, header: str) -> bool:
        return header in self.headers

    def __getitem__(self, header: str) -> str:
        return self.headers[header][0]

    def __setitem__(self, header: str, value: str):
        self.headers[header] = value


class MiddlewareTestCase(TestCase):
    # noinspection PyMethodMayBeStatic
    def test_middleware_basics(self):
        fake_requests = FakeRequest()
        world_ = "Hello World" * 420
        fake_response = FakeResponse(content=world_)

        brotli_middleware = BrotliMiddleware()
        brotli_response = brotli_middleware.process_response(fake_requests, fake_response)

        decom = brotli.decompress(data=brotli_response.content)  # type: bytes
        self.assertEqual(world_, decom.decode(encoding='utf-8'))
