import gzip
from collections.abc import Callable
from typing import ClassVar, MutableMapping, Optional

import brotli
import pytest
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from faker import Faker

from django_brotli.middleware import MIN_LEN_FOR_RESPONSE_TO_PROCESS, BrotliMiddleware


class FakeRequestAcceptsBrotli:
    META: ClassVar[dict[str, str]] = {"HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch, br"}


class FakeLegacyRequest:
    META: ClassVar[dict[str, str]] = {"HTTP_ACCEPT_ENCODING": "gzip, deflate, sdch"}


class FakeResponse:
    streaming: bool = False
    content: bytes
    headers: MutableMapping[str, str]

    def __init__(
        self,
        content: str,
        headers: Optional[MutableMapping[str, str]] = None,
        streaming: Optional[bool] = None,
    ) -> None:
        self.content = content.encode(encoding="utf-8")
        self.headers = headers or {}

        if streaming:
            self.streaming = streaming

    def has_header(self, header: str) -> bool:
        return header in self.headers

    def get(self, key: str) -> Optional[str]:
        return self.headers.get(key)

    def __getitem__(self, header: str) -> str:
        return self.headers[header]

    def __setitem__(self, header: str, value: str) -> None:
        self.headers[header] = value


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()


@pytest.fixture
def sample_text(faker: Faker) -> str:
    """Generate a long text suitable for compression testing"""
    return " ".join(faker.paragraphs(nb=20))


@pytest.fixture
def short_text(faker: Faker) -> str:
    """Generate a short text that shouldn't be compressed"""
    return faker.sentence()


@pytest.fixture
def fake_request() -> FakeRequestAcceptsBrotli:
    return FakeRequestAcceptsBrotli()


@pytest.fixture
def fake_legacy_request() -> FakeLegacyRequest:
    return FakeLegacyRequest()


@pytest.fixture
def get_response(sample_text: str) -> Callable[[HttpRequest], HttpResponse]:
    def _get_response(request: HttpRequest) -> HttpResponse:
        return FakeResponse(content=sample_text)

    return _get_response


@pytest.fixture
def brotli_middleware(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> BrotliMiddleware:
    return BrotliMiddleware(get_response=get_response)


def test_middleware_compress_response(
    fake_request: FakeRequestAcceptsBrotli,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
) -> None:
    fake_response = FakeResponse(content=sample_text)
    brotli_response = brotli_middleware.process_response(fake_request, fake_response)
    decompressed_response = brotli.decompress(brotli_response.content)

    assert sample_text == decompressed_response.decode(encoding="utf-8")
    assert brotli_response.get("Content-Encoding") == "br"


@pytest.fixture
def streaming_sequence(faker: Faker) -> list[bytes]:
    """Generate a sequence of realistic text chunks for streaming tests"""
    return [
        faker.paragraph(nb_sentences=50).encode("utf-8"),  # Long chunk
        faker.text(max_nb_chars=200).encode("utf-8"),  # Medium chunk
        faker.paragraph(nb_sentences=30).encode("utf-8"),  # Another chunk
    ]


def test_compress_streaming_response(
    fake_request: FakeRequestAcceptsBrotli,
    get_response: Callable[[HttpRequest], HttpResponse],
    streaming_sequence: list[bytes],
) -> None:
    """Test that streaming content is properly compressed"""

    def get_stream_response() -> StreamingHttpResponse:
        resp = StreamingHttpResponse(streaming_sequence)
        resp["Content-Type"] = "text/html; charset=UTF-8"
        return resp

    fake_response = get_stream_response()
    brotli_middleware = BrotliMiddleware(get_response=get_response)
    brotli_response = brotli_middleware.process_response(fake_request, fake_response)

    # Collect all streaming content
    compressed_content = b"".join(brotli_response.streaming_content)
    decompressed_response = brotli.decompress(compressed_content)

    assert b"".join(streaming_sequence) == decompressed_response
    assert brotli_response.get("Content-Encoding") == "br"
    assert not brotli_response.has_header("Content-Length")


def test_etag_is_updated_if_present(
    fake_request: FakeRequestAcceptsBrotli,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
) -> None:
    fake_etag_content = '"foo"'
    fake_response = FakeResponse(
        content=sample_text, headers={"ETag": fake_etag_content}
    )

    assert fake_response["ETag"] == fake_etag_content

    brotli_response = brotli_middleware.process_response(fake_request, fake_response)
    decompressed_response = brotli.decompress(brotli_response.content)

    assert sample_text == decompressed_response.decode(encoding="utf-8")
    assert brotli_response["ETag"] == '"foo;br\\"'


def test_middleware_wont_compress_response_if_response_is_small(
    fake_request: FakeRequestAcceptsBrotli,
    brotli_middleware: BrotliMiddleware,
    short_text: str,
) -> None:
    assert len(short_text) < MIN_LEN_FOR_RESPONSE_TO_PROCESS

    fake_response = FakeResponse(content=short_text)
    brotli_response = brotli_middleware.process_response(fake_request, fake_response)

    assert short_text == brotli_response.content.decode(encoding="utf-8")
    assert "Content-Encoding" not in brotli_response.headers


def test_middleware_wont_compress_if_client_not_accept(
    fake_legacy_request: FakeLegacyRequest,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
) -> None:
    fake_response = FakeResponse(content=sample_text)
    brotli_response = brotli_middleware.process_response(
        fake_legacy_request, fake_response
    )

    assert sample_text == brotli_response.content.decode(encoding="utf-8")
    assert "Content-Encoding" not in brotli_response.headers


def test_middleware_wont_compress_if_response_is_already_compressed(
    fake_request: FakeRequestAcceptsBrotli,
    get_response: Callable[[HttpRequest], HttpResponse],
    sample_text: str,
) -> None:
    from django.middleware.gzip import GZipMiddleware

    fake_response = FakeResponse(content=sample_text)

    brotli_middleware = BrotliMiddleware(get_response=get_response)
    django_gzip_middleware = GZipMiddleware(get_response=get_response)

    gzip_response = django_gzip_middleware.process_response(fake_request, fake_response)
    brotli_response = brotli_middleware.process_response(fake_request, gzip_response)

    assert sample_text == gzip.decompress(brotli_response.content).decode(
        encoding="utf-8"
    )


@pytest.mark.parametrize("content_encoding", ["gzip", "br", "deflate", "compress"])
def test_middleware_skips_already_compressed_content(
    fake_request: FakeRequestAcceptsBrotli,
    brotli_middleware: BrotliMiddleware,
    sample_text: str,
    content_encoding: str,
) -> None:
    """Test that middleware skips processing if any compression is already applied"""
    fake_response = FakeResponse(
        content=sample_text, headers={"Content-Encoding": content_encoding}
    )

    response = brotli_middleware.process_response(fake_request, fake_response)
    assert response.get("Content-Encoding") == content_encoding
    assert sample_text == response.content.decode(encoding="utf-8")
