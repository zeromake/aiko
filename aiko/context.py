# -*- coding: utf-8 -*-

import asyncio

from .request import Request
from .response import Response

__all__ = [
    "Context",
]


class Context(object):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        request: Request,
        response: Response,
    ) -> None:
        self._loop = loop
        self._request = request
        self._response = response

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def request(self) -> Request:
        return self._request

    @property
    def response(self) -> Response:
        return self._response
