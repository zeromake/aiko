# -*- coding: utf-8 -*-

import asyncio
from socket import socket as sys_socket
from typing import Any, Callable, cast, Dict, Generator, List, Optional, Union
from urllib.parse import parse_qs, unquote, urlencode
# from datetime import datetime

from httptools import HttpRequestParser, parse_url

from .cookies import Cookies
from .utils import (
    decode_bytes,
    DEFAULT_REQUEST_CODING,
    encode_str,
    fresh,
    HEADER_TYPE,
    STATIC_METHODS,
)

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


class RequestUrl(object):
    def __init__(self, href: bytes, coding: str = "utf-8") -> None:
        url = parse_url(href)
        self.coding = coding
        self.schema = decode_bytes(url.schema, coding)
        self.host = decode_bytes(url.host, coding)
        self.port = cast(Optional[int], url.port)
        self.path = cast(Optional[str], self.decode_bytes(url.path))
        self.querystring = cast(Optional[str], self.decode_bytes(url.query))
        self.fragment = cast(Optional[str], self.decode_bytes(url.fragment))
        self.userinfo = cast(Optional[str], self.decode_bytes(url.userinfo))

    def decode_bytes(self, data: Optional[bytes]) -> Optional[str]:
        if data is not None:
            return decode_bytes(data, self.coding)
        return None

    @property
    def query(self) -> Optional[RequestParameters]:
        if self.querystring is not None:
            return RequestParameters(parse_qs(self.querystring))
        return None

    @query.setter
    def query(self, query_obj: Dict[str, str]) -> None:
        self.querystring = urlencode(query_obj)

    @property
    def raw_query(self) -> Optional[Dict[str, str]]:
        query_obj = self.query
        if query_obj is not None:
            return {
                k: v[0] for k, v in query_obj.items() if v is not None and len(v) > 1
            }
        return None

    @property
    def href(self) -> str:
        """
        把 url 从新构建
        """
        href_arr = cast(List[str], [])
        href_arr.append(self.schema)
        href_arr.append("://")
        if self.userinfo is not None:
            href_arr.append(self.userinfo)
            href_arr.append("@")
        href_arr.append(self.host)
        if self.port is not None:
            href_arr.append(":%d" % self.port)
        if self.path is not None:
            href_arr.append(self.path)
        if self.querystring is not None:
            href_arr.append("?")
            href_arr.append(self.querystring)
        if self.fragment is not None:
            href_arr.append("#")
            href_arr.append(self.fragment)
        href_str = "".join(href_arr)
        return href_str


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
        "_cookies",
        "_host",
        "_ssl",
        "_app",
        "_transport",
        "_socket",
        "_default_charset",
        "response",
        "ctx",
        # "start_time"
    ]

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            handle: Callable[
                [],
                Generator[Any, None, None],
            ],
            transport: Optional[asyncio.Transport] = None,
            charset: str = DEFAULT_REQUEST_CODING,
    ) -> None:
        self._loop = loop
        self._headers = cast(HEADER_TYPE, {})
        self._current_url = b""
        self._handle = handle
        self._parser = cast(HttpRequestParser, None)
        self._method = cast(Optional[str], None)
        self._version = cast(Optional[str], None)
        self._length = cast(Optional[int], None)
        self._URL = cast(Optional[RequestUrl], None)
        self._cookies = Cookies()
        self._host = ""
        self._ssl = bool(transport is not None and transport.get_extra_info('sslcontext'))
        self._socket = cast(
            Optional[sys_socket],
            transport and transport.get_extra_info('socket'),
        )
        self._transport = transport
        self._app = cast(Any, None)
        self._default_charset = charset
        self.response = cast(Any, None)
        self.ctx = cast(Any, None)

    @property
    def default_charset(self) -> str:
        return self._default_charset

    @default_charset.setter
    def default_charset(self, charset: str) -> None:
        self._default_charset = charset

    @property
    def _get_charset(self) -> str:
        """
        获取默认编码
        """
        return self.charset or self.default_charset

    # ----HttpRequestParser method------
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

    def on_header(self, name: bytes, value: bytes) -> None:
        """
        header 回调
        """
        name_ = decode_bytes(name).casefold()
        val = decode_bytes(value)
        if name_ == "cookie":
            # 加载上次的 cookie
            self._cookies.load(val)
        if name_ in self._headers:
            # 多个相同的 header
            old = self._headers[name_]
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

    @method.setter
    def method(self, val: str) -> None:
        """
        重写请求方法
        """
        self._method = val

    @property
    def version(self) -> Optional[str]:
        """
        获取 http 版本
        """
        if self._version is None:
            self._version = self._parser.get_http_version()
        return self._version

    # 仿 koa api
    @property
    def app(self) -> Any:
        """
        web app 用与获取配置
        """
        return self._app

    @app.setter
    def app(self, app: Any) -> None:
        """
        设置app到
        """
        self._app = app

    @property
    def proxy(self) -> bool:
        """
        从 app 读取是否判断 proxy
        """
        if self.app is None:
            return False
        return bool(cast(Any, self.app).proxy)

    @property
    def socket(self) -> Optional[sys_socket]:
        """
        原生 socket
        """
        return self._socket

    @property
    def length(self) -> Optional[int]:
        """
        获取 body 长度
        """
        len_ = self.get("content-length")
        if len_ is not None:
            return int(cast(str, len_))
        return None

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
    def url(self) -> str:
        """
        path + query 的url
        """
        url_str = self.parse_url.path or ""
        if self.parse_url.querystring is not None:
            url_str += "?" + self.parse_url.querystring
        return url_str

    @url.setter
    def url(self, url_str: str) -> None:
        """
        url 重写
        """
        if "?" in url_str:
            url_arr = url_str.split("?")
            self.parse_url.path = url_arr[0]
            self.parse_url.querystring = url_arr[1]

    @property
    def path(self) -> Optional[str]:
        """
        获取 path
        """
        path_str = self.parse_url.path
        if path_str is not None and "%" in path_str:
            path_str = unquote(path_str)
        return path_str

    @path.setter
    def path(self, path_str: str) -> None:
        """
        重写 path
        """
        self.parse_url.path = path_str

    @property
    def query(self) -> Optional[RequestParameters]:
        """
        获取query字典对象
        """
        return self.parse_url.query

    @query.setter
    def query(self, query_dict: Dict[str, Any]) -> None:
        """
        重写 query
        """
        self.parse_url.query = cast(Any, query_dict)

    @property
    def querystring(self) -> Optional[str]:
        """
        获取 query string
        """
        return self.parse_url.querystring

    @querystring.setter
    def querystring(self, query_str: str) -> None:
        """
        重写 query string
        """
        self.parse_url.querystring = query_str

    @property
    def search(self) -> Optional[str]:
        """
        querystring 别名
        """
        return self.querystring

    @search.setter
    def search(self, query_str: str) -> None:
        """
        重写 querystring
        """
        self.parse_url.querystring = query_str

    @property
    def origin(self) -> str:
        """
        获取 url 来源，包括 schema 和 host
        """
        return "%s://%s" % (self.parse_url.schema, self.parse_url.host)

    @property
    def href(self) -> str:
        """
        全量url
        """
        return self.parse_url.href

    @property
    def parse_url(self) -> RequestUrl:
        """
        获取url解析对象
        """
        if self._URL is None:
            current_url = b"%s://%s%s" % (
                encode_str(self.schema),
                encode_str(self.host),
                self._current_url
            )
            self._URL = RequestUrl(current_url)
        return cast(RequestUrl, self._URL)

    @property
    def original_url(self) -> str:
        """
        原始 url
        """
        return decode_bytes(
            self._current_url,
            self._get_charset,
        )

    @property
    def schema(self) -> str:
        """
        返回请求协议，“https” 或 “http”。
        当 app.proxy 是 true 时支持 X-Forwarded-Proto。
        """
        if self._ssl:
            return "https"
        proxy = bool(self.app and self.app.proxy)
        if not proxy:
            return "http"
        proto = cast(str, self.get("X-Forwarded-Proto") or "http")
        return proto.split(",")[0].strip()

    @property
    def protocol(self) -> str:
        """
        返回请求协议，“https” 或 “http”。
        当 app.proxy 是 true 时支持 X-Forwarded-Proto。
        """
        return self.schema

    @property
    def secure(self) -> bool:
        """
        通过 request.schema == "https" 来检查请求是否通过 TLS 发出
        """
        return self.schema == "https"

    @property
    def charset(self) -> Optional[str]:
        """
        获取 charset
        """
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
        """
        获取 type
        """
        type_str = cast(Optional[str], self.get("Content-Type"))
        if type_str is not None:
            return type_str.split(";")[0]
        else:
            return None

    @property
    def host(self) -> str:
        """
        获取 host + port, 如果开启 proxy 开关。使用 X-Forwarded-Host 头
        """
        host = cast(Optional[str], None)
        if self.proxy and 'X-Forwarded-Host' in self._headers:
            xhost = cast(Optional[str], self.get('X-Forwarded-Host'))
            if xhost is not None:
                host = xhost.split(",")[0].strip()
        host = host or cast(str, self.get('Host'))
        return host

    @property
    def hostname(self) -> str:
        """
        去掉端口的域名或ip
        """
        return self.host.split(":")[0]

    @property
    def ips(self) -> Optional[List[str]]:
        """
        获取远端代理ip
        """
        if self.proxy and "X-Forwarded-For" in self._headers:
            val = cast(str, self.get('X-Forwarded-For'))
            ips = [i.strip() for i in val.split(",")]
            return ips if len(ips) > 0 else None
        return None

    @property
    def ip(self) -> Optional[str]:
        """
        获取客户端ip， 开启代理会从 X-Forwarded-For 中获取
        """
        ips = self.ips
        if ips and len(ips) > 0:
            return ips[0]
        if self._transport:
            return cast(
                str,
                self._transport.get_extra_info("peername"),
            )
        return None

    @property
    def cookies(self) -> Cookies:
        """
        在 on_headers_complete 回调后可以获得这次请求的 cookie
        """
        return self._cookies

    @property
    def headers(self) -> HEADER_TYPE:
        """
        在 on_headers_complete 回调后可以获得这次请求的 headers
        """
        return self._headers

    @property
    def header(self) -> HEADER_TYPE:
        """
        headers 的别名
        """
        return self._headers

    @property
    def fresh(self) -> bool:
        """
        检查请求缓存是否“新鲜”，也就是内容没有改变。
        此方法用于 If-None-Match / ETag, 和 If-Modified-Since 和 Last-Modified 之间的缓存协商。
        在设置一个或多个这些响应头后应该引用它。
        """
        method_str = self.method
        if method_str != 'GET' and method_str != 'HEAD':
            return False
        s = self.ctx.status
        if (s >= 200 and s < 300) or s == 304:
            return fresh(
                self.headers,
                (self.response and self.response.headers) or {},
            )
        return False

    @property
    def stale(self) -> bool:
        """
        与 fresh 相反
        """
        return not self.fresh

    @property
    def idempotent(self) -> bool:
        """
        检查请求是否是幂等的。
        """
        return bool(~(STATIC_METHODS.index(self.method)))
