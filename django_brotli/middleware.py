# -*- encoding: utf-8 -*-
# ! python3

import re

import brotli
from django.utils.cache import patch_vary_headers

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

RE_ACCEPT_ENCODING_BROTLI = re.compile(r'\bbr\b')


class BrotliMiddleware(MiddlewareMixin):
    """
    This middleware compresses content if the browser allows `brotli` compression.
    It sets the Vary header accordingly, so that caches will base their storage
    on the Accept-Encoding header. Code of this middleware is based on Django's `GZipMiddleware`.
    """

    # noinspection PyMethodMayBeStatic
    def process_response(self, request, response):
        if any(
            (response.streaming,
             response.has_header('Content-Encoding'),
             not RE_ACCEPT_ENCODING_BROTLI.search(request.META.get('HTTP_ACCEPT_ENCODING', '')),
             len(response.content) < 200)):
            # ---------
            # 1) brotlipy doesn't support streaming compression, see: https://github.com/google/brotli/issues/191
            # 2) Avoid brotli if we've already got a content-encoding.
            # 3) Client doesn't support brotli
            # 4) It's not worth attempting to compress really short responses.
            #    This was taken from django GZipMiddleware.
            # ---------
            return response

        patch_vary_headers(response, ('Accept-Encoding',))
        compressed_content = brotli.compress(response.content)

        # Return the compressed content only if it's actually shorter.
        if len(compressed_content) >= len(response.content):
            return response

        response.content = compressed_content
        response['Content-Length'] = str(len(response.content))

        if response.has_header('ETag'):
            response['ETag'] = re.sub('"$', ';br"', response['ETag'])

        response['Content-Encoding'] = 'br'

        return response
