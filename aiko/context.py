# -*- coding: utf-8 -*-

import asyncio
from typing import Any, List, Optional

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
        self._cookies = ContextCookie(self)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def request(self) -> Request:
        return self._request

    @property
    def response(self) -> Response:
        return self._response

    @property
    def cookies(self) -> 'ContextCookie':
        return self._cookies


class ContextCookie(dict):
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx
        self._req_cookies = ctx.request.cookies
        self._res_cookies = ctx.response.cookies

    def __delitem__(self, key: str) -> None:
        del self._res_cookies[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._res_cookies[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._req_cookies[key]

    def __iter__(self) -> Any:
        return iter(self._req_cookies)

    def __len__(self) -> int:
        return len(self._req_cookies)

    def __contains__(self, key: Any) -> bool:
        return key in self._req_cookies

    def get(self, key: Any, default: Any = None) -> Any:
        return self._req_cookies.get(key, default)

    def set(self, key: str, value: str, opt: dict = None) -> None:
        self._res_cookies.set(key, value, opt)

    def headers(self) -> Optional[List[str]]:
        return self._res_cookies.headers()
