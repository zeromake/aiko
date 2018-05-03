# -*- coding: utf-8 -*-

import asyncio
from typing import Any, Callable, Dict, Generator, Optional
# from datetime import datetime

from httptools import HttpRequestParser, parse_url

from .utils import decode_bytes, encode_str

__all__ = [
    "Request",
]


class Request(object):
    __slots__ = [
        "_loop",
        "_headers",
        "_current_url",
        "_handle",
        "_parser",
        "_method",
        "_version",
        "_length",
        "_URL",
        "_original_url",
        # "start_time"
    ]

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop],
        handle: Callable[
            [],
            Generator[Any, None, None],
        ],
    ) -> None:
        self._loop = loop
        self._headers: Dict[str, str] = {}
        self._current_url: Optional[str] = None
        self._handle = handle
        self._parser: Optional[HttpRequestParser] = None
        self._method: Optional[str] = None
        self._version: Optional[str] = None
        self._length: Optional[int] = None
        self._URL = None
        self._original_url: Optional[str] = None

    @property
    def url(self) -> str:
        return self._current_url

    @url.setter
    def url(self, url: str) -> None:
        self._URL = parse_url(encode_str(url))
        self._current_url = url

    @property
    def original_url(self) -> str:
        return self._original_url or self._current_url

    @property
    def parser(self) -> HttpRequestParser:
        return self._parser

    @parser.setter
    def parser(self, parser: HttpRequestParser) -> None:
        if self._parser is None:
            self._parser = parser

    def feed_data(self, data: bytes) -> None:
        """
        代理 feed_data
        """
        self._parser.feed_data(data)

    @property
    def should_keep_alive(self) -> bool:
        return self._parser.should_keep_alive()

    def on_url(self, url: bytes) -> None:
        """
        httptools url callback
        """
        self._URL = parse_url(url)
        self._current_url = decode_bytes(url)
        self._original_url = self._current_url

    def on_header(self, name: bytes, value: bytes) -> None:
        name_ = decode_bytes(name).casefold()
        if name_ == "content-length":
            self._length = int(decode_bytes(value))
        self._headers[name_] = decode_bytes(value)

    def on_headers_complete(self) -> None:
        self._loop.create_task(self._handle())
        return None

    @property
    def method(self) -> str:
        if self._method is None:
            self._method = decode_bytes(self._parser.get_method())
        return self._method

    @property
    def version(self) -> str:
        if self._version is None:
            self._version = self._parser.get_http_version()
        return self._version

    @property
    def length(self) -> int:
        return self._length
