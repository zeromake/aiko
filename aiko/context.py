# -*- coding: utf-8 -*-

import asyncio
from typing import Any, List, Optional
# from weakref import proxy

from .request import Request
from .response import Response
from .utils import ProxyAttr


__all__ = [
    "Context",
]


class Context(object):
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            request: Request,
            response: Response,
            app: Any,
    ) -> None:
        self._loop = loop
        self._request = request
        self._response = response
        self._cookies = ContextCookie(self)
        self._app = app

    @property
    def app(self) -> Any:
        return self._app

    @app.setter
    def app(self, app: Any) -> None:
        self._app = app

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

    def __del__(self) -> None:
        del self._cookies
        del self._request
        del self._response
        del self._loop


ProxyAttr(Context, '_response')\
    .method('set')\
    .method('flush_headers')\
    .access('status')\
    .access('message')\
    .access('body')\
    .access('length')\
    .access('type')\
    .getter('header_sent')

ProxyAttr(Context, '_request')\
    .method('get')\
    .access('querystring')\
    .access('querystring', 'search')\
    .access('method')\
    .access('query')\
    .access('path')\
    .access('url')\
    .getter('origin')\
    .getter('href')\
    .getter('protocol')\
    .getter('protocol', 'schema')\
    .getter('host')\
    .getter('hostname')\
    .getter('headers')\
    .getter('headers', 'header')\
    .getter('secure')\
    .getter('ips')\
    .getter('socket')\
    .getter('ip')


class ContextCookie(dict):
    """
    重载 `ctx.request.cookies` and `ctx.response.cookies`。
    读取使用 `ctx.request.cookies`
    写入使用 `ctx.response.cookies`
    """
    def __init__(self, ctx: Context) -> None:
        # self._ctx = proxy(ctx)
        self._req_cookies = ctx.request.cookies
        self._res_cookies = ctx.response.cookies

    def __delitem__(self, key: str) -> None:
        """
        设置删除 cookie 到 res
        """
        del self._res_cookies[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        设置一个 cookie 到 res
        """
        self._res_cookies[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        获取一个 cookie 从 res
        """
        return self._req_cookies[key]

    def __iter__(self) -> Any:
        """
        遍历 req cookies
        """
        return iter(self._req_cookies)

    def __len__(self) -> int:
        """
        查看 req 的cookie有多少个
        """
        return len(self._req_cookies)

    def __contains__(self, key: Any) -> bool:
        """
        判断一个 key 是否在 cookies 中
        """
        return key in self._req_cookies

    def get(self, key: Any, default: Any = None) -> Any:
        """
        读取使用 req like koa
        """
        return self._req_cookies.get(key, default)

    def set(self, key: str, value: str, opt: dict = None) -> None:
        """
        写入使用 res like koa
        """
        self._res_cookies.set(key, value, opt)

    def headers(self) -> Optional[List[str]]:
        """
        序列化出 cookies 的header
        """
        return self._res_cookies.headers()
