# -*- coding: utf-8 -*-
"""
处理socket，生成 req，res
"""

import asyncio
from typing import Any, Callable, cast, Generator, Optional

from httptools import HttpRequestParser

from .request import Request
from .response import Response
from .utils import (
    DEFAULT_HTTP_VERSION,
    DEFAULT_REQUEST_CODING,
    DEFAULT_RESPONSE_CODING,
)

__all__ = ["ServerProtocol"]


class ServerProtocol(asyncio.Protocol):
    """
    http Protocol
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
            requset_charset: str = DEFAULT_REQUEST_CODING,
            response_charset: str = DEFAULT_RESPONSE_CODING,
    ) -> None:
        self._loop = loop
        self._transport = cast(Optional[asyncio.Transport], None)
        self._request = cast(Optional[Request], None)
        self._response = cast(Optional[Response], None)
        self._handle = handle
        self._requset_charset = requset_charset
        self._response_charset = response_charset

    def connection_made(self, transport: Any) -> None:
        """
        Called when a connection is made.
        """
        self._transport = transport

    def connection_lost(self, exc: Exception) -> None:
        """
        socket 断开连接
        """
        self._transport = None
        self._request = None
        # self._request_parser = None

    def data_received(self, data: bytes) -> None:
        """
        socket 收到数据
        """
        # print(data)
        if self._request is None:
            # future = self._loop.create_future()
            self._request = Request(
                cast(asyncio.AbstractEventLoop, self._loop),
                self.complete_handle,
                cast(asyncio.Transport, self._transport),
                charset=self._requset_charset,
            )
            self._request.parser = HttpRequestParser(self._request)
        self._request.feed_data(data)

    @asyncio.coroutine
    def complete_handle(self) -> Generator[Any, None, None]:
        """
        完成回调
        """
        if self._request is None:
            return
        self._response = Response(
            self._loop,
            cast(asyncio.Transport, self._transport),
            self._request.version or DEFAULT_HTTP_VERSION,
            self._response_charset,
        )
        keep_alive = self._request.should_keep_alive
        if not keep_alive:
            self._response.set("Connection", "close")
        yield from self._handle(self._request, self._response)
        if not keep_alive and self._transport is not None:
            self._transport.close()
        # self._request_parser = None
        self._request = None
        self._response = None
