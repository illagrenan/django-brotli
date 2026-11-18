"""Middleware that compresses response using brotli algorithm."""

from .middleware import (
    BROTLI_MODE,
    BROTLI_QUALITY,
    MIN_LEN_FOR_RESPONSE_TO_PROCESS,
    BrotliMiddleware,
    acompress_stream,
    compress,
    compress_stream,
)

__author__ = """Václav Dohnal"""
__email__ = "vaclav.dohnal@gmail.com"
__version__ = "0.4.0"


__all__ = [
    "BROTLI_MODE",
    "BROTLI_QUALITY",
    "MIN_LEN_FOR_RESPONSE_TO_PROCESS",
    "BrotliMiddleware",
    "__version__",
    "acompress_stream",
    "compress",
    "compress_stream",
]
