# -*- coding: utf-8 -*-

import asyncio
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Union
from urllib.parse import parse_qs
# from datetime import datetime

from httptools import HttpRequestParser, parse_url

from .cookies import Cookies
from .utils import decode_bytes, encode_str

__all__ = [
    "Request",
]


class RequestParameters(dict):
    """Hosts a dict with lists as values where get returns the first
    value of the list and getlist returns the whole shebang
    """

    def get(self, name: str, default: Any = None) -> Any:
        """Return the first value, either the default or actual"""
        return super().get(name, [default])[0]

    def getlist(self, name: str, default: Any = None) -> List[Any]:
        """Return the entire list"""
        return super().get(name, default)


class Request(object):
    """
    请求
    """
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
        "_cache",
        "_cookies",
        "_host",
        "_schema",
        "_ssl",
        "_app",
        # "start_time"
    ]

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        handle: Callable[
            [],
            Generator[Any, None, None],
        ],
        ssl: bool = False,
    ) -> None:
        self._loop = loop
        self._headers: Dict[str, Union[str, List[str]]] = {}
        self._current_url: bytes = b""
        self._handle = handle
        self._parser: HttpRequestParser = cast(HttpRequestParser, None)
        self._method: Optional[str] = None
        self._version: Optional[str] = None
        self._length: Optional[int] = None
        self._URL: Any = None
        self._original_url: Optional[bytes] = None
        self._cache: Dict[str, Any] = {}
        self._cookies = Cookies()
        self._host = ""
        self._ssl = ssl
        self._schema = "https" if ssl else "http"
        self._app: Any = None

    @property
    def app(self) -> Any:
        return self._app

    @app.setter
    def app(self, app: Any) -> None:
        self._app = app

    @property
    def proxy(self) -> bool:
        if self.app is None:
            return False
        return cast(Any, self.app).proxy

    @property
    def url(self) -> str:
        """
        全部url
        """
        return decode_bytes(self._current_url, 'utf8')

    @url.setter
    def url(self, url: str) -> None:
        """
        url 重写
        """
        if self._URL is not None:
            self._URL = None
        self._current_url = encode_str(url, 'utf8')

    @property
    def href(self) -> str:
        return "%s://%s%s" % (
            self._schema,
            self._host,
            decode_bytes(self._current_url, 'utf8'),
        )

    @property
    def parse_url(self) -> Any:
        if self._URL is None:
            current_url = b"%s://%s%s" % (
                encode_str(self._schema),
                encode_str(self._host),
                self._current_url
            )
            self._URL = parse_url(current_url)
        return self._URL

    @property
    def original_url(self) -> str:
        """
        原始 url
        """
        return decode_bytes(self._original_url or self._current_url, 'utf8')

    @property
    def origin(self) -> str:
        """
        获取 url 来源，包括 schema 和 host
        """
        return "%s://%s" % (self._schema, self._host)

    @property
    def parser(self) -> Optional[HttpRequestParser]:
        """
        httptools.HttpRequestParser 对象
        """
        return self._parser

    @parser.setter
    def parser(self, parser: HttpRequestParser) -> None:
        """
        由于这个对象实例化需要作为 HttpRequestParser 所以只能后面设置
        """
        if self._parser is None:
            self._parser = parser

    def feed_data(self, data: bytes) -> None:
        """
        代理 feed_data
        """
        if self._parser is not None:
            self._parser.feed_data(data)

    @property
    def should_keep_alive(self) -> Optional[bool]:
        """
        判断是否为 keep_alive 是开启长连接
        """
        if self._parser is not None:
            return self._parser.should_keep_alive()
        return None

    def on_url(self, url: bytes) -> None:
        """
        httptools url callback
        """
        self._current_url = url
        self._original_url = url

    def on_header(self, name: bytes, value: bytes) -> None:
        """
        header 回调
        """
        name_ = decode_bytes(name).casefold()
        val = decode_bytes(value)
        if name_ == "content-length":
            # 设置 content-length
            self._length = int(val)
        elif name_ == "cookie":
            # 加载上次的 cookie
            self._cookies.load(val)
        elif name_ == "host":
            self._host = val
        if name_ in self._headers:
            # 多个相同的 header
            old: Union[str, List[str]] = self._headers[name_]
            if isinstance(old, list):
                old.append(val)
            else:
                self._headers[name_] = [old, val]
        else:
            self._headers[name_] = val

    def on_headers_complete(self) -> None:
        """
        header 回调完成
        """
        self._loop.create_task(self._handle())

    @property
    def method(self) -> str:
        """
        获取请求方法
        """
        if self._method is None:
            self._method = decode_bytes(self._parser.get_method())
        return self._method

    @property
    def version(self) -> Optional[str]:
        """
        获取 http 版本
        """
        if self._version is None:
            self._version = self._parser.get_http_version()
        return self._version

    @property
    def length(self) -> Optional[int]:
        """
        获取 body 长度
        """
        return self._length

    def get(self, name: str) -> Union[None, str, List[str]]:
        """
        获取 header
        """
        name = name.casefold()
        if name == "referer" or name == "referrer":
            if "referrer" in self._headers:
                return self._headers["referrer"]
            elif "referer" in self._headers:
                return self._headers["referer"]
            else:
                return None
        elif name in self._headers:
            return self._headers[name]
        else:
            return None

    def set(self, name: str, value: str) -> None:
        """
        重写请求中的 header, 不推荐使用
        """
        name = name.casefold()
        self._headers[name] = value

    @property
    def path(self) -> str:
        """
        获取 path
        """
        path = decode_bytes(self.parse_url.path, 'utf8')
        return path

    @property
    def query(self) -> Dict[str, List[str]]:
        """
        获取query字典对象
        """
        return RequestParameters(parse_qs(self.querystring))

    @property
    def querystring(self) -> str:
        """
        获取 path
        """
        querystring = decode_bytes(self.parse_url.query, 'utf8')
        return querystring

    @property
    def search(self) -> str:
        return self.querystring

    @property
    def schema(self) -> str:
        return self._schema

    @property
    def secure(self) -> bool:
        return self._ssl

    @property
    def charset(self) -> Optional[str]:
        type_str = cast(str, self.get("Content-Type"))
        if type_str is None or "charset" not in type_str:
            return None
        for i in type_str.split(";"):
            item = i.strip()
            if item.startswith("charset"):
                return item.split("=")[1].strip()
        return None

    @property
    def type(self) -> Optional[str]:
        type_str = cast(Optional[str], self.get("Content-Type"))
        if type_str is not None:
            return type_str.split(";")[0]
        else:
            return None

    @property
    def host(self) -> str:
        host = self.proxy and cast(str, self.get('X-Forwarded-Host'))
        host = host or cast(str, self.get('Host'))
        if not host:
            return ""
        return host.split(",")[0].strip()

    @property
    def hostname(self) -> str:
        return self.host.split(":")[0]

    @property
    def ips(self) -> List[str]:
        val = cast(str, self.get('X-Forwarded-For'))
        if self.proxy and val:
            return [i.strip() for i in val.split(",")]
        return []

    @property
    def cookies(self) -> Cookies:
        """
        在 on_headers_complete 回调后可以获得这次请求的 cookie
        """
        return self._cookies

    @property
    def headers(self) -> Dict[str, Union[str, List[str]]]:
        """
        在 on_headers_complete 回调后可以获得这次请求的 headers
        """
        return self._headers

    @property
    def header(self) -> Dict[str, Union[str, List[str]]]:
        """
        headers 的别名
        """
        return self._headers
