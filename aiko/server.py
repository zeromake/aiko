# -*- coding: utf-8 -*-

import asyncio
from typing import Any, Callable, Generator, Optional

from httptools import HttpRequestParser

from .request import Request
from .response import Response

__all__ = ["ServerProtocol"]


class ServerProtocol(asyncio.Protocol):
    """

    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        handle: Callable[
            [
                Request,
                Response,
            ],
            Generator[Any, None, None],
        ],
    ) -> None:
        self._loop = loop
        self._transport: Optional[asyncio.Transport] = None
        self._request: Optional[Request] = None
        self._response: Optional[Response] = None
        self._handle = handle

    def connection_made(self, transport: Any) -> None:
        """
        Called when a connection is made.
        """
        self._transport = transport

    def connection_lost(self, exc: Exception) -> None:
        self._transport = None
        self._request = None
        # self._request_parser = None

    def data_received(self, data: bytes) -> None:
        if self._request is None:
            # future = self._loop.create_future()
            self._request = Request(self._loop, self.complete_handle)
            self._request.parser = HttpRequestParser(self._request)
        self._request.feed_data(data)

    @asyncio.coroutine
    def complete_handle(self) -> Generator[Any, None, None]:
        self._response = Response(self._loop, self._transport)
        keep_alive = self._request.should_keep_alive
        if not keep_alive:
            self._response.set("Connection", "close")
        yield from self._handle(self._request, self._response)
        if not keep_alive:
            self._transport.close()
        # self._request_parser = None
        self._request = None
