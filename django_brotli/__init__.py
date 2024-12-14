# -*- encoding: utf-8 -*-
# ! python3

"""Middleware that compresses response using brotli algorithm."""

from __future__ import annotations

from .middleware import (
    BROTLI_MODE,
    BROTLI_QUALITY,
    MIN_LEN_FOR_RESPONSE_TO_PROCESS,
    BrotliMiddleware,
    compress,
)

__author__ = """Václav Dohnal"""
__email__ = "vaclav.dohnal@gmail.com"
__version__ = "0.3.0"


__all__ = [
    "BROTLI_MODE",
    "BROTLI_QUALITY",
    "MIN_LEN_FOR_RESPONSE_TO_PROCESS",
    "BrotliMiddleware",
    "__version__",
    "compress",
]
