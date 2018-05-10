# -*- coding: utf-8 -*-
"""
响应
"""

import asyncio
import json
import os
from io import RawIOBase
from socket import socket
from typing import Any, cast, Dict, List, Optional, Union

from .cookies import Cookies
from .utils import (
    DEFAULT_HTTP_VERSION,
    DEFAULT_RESPONSE_CODING,
    encode_str,
    HEADER_TYPE,
)

__all__ = [
    "STATUS_CODES",
    "Response",
]

STATUS_CODES = {
    100: b'Continue',
    101: b'Switching Protocols',
    102: b'Processing',
    200: b'OK',
    201: b'Created',
    202: b'Accepted',
    203: b'Non-Authoritative Information',
    204: b'No Content',
    205: b'Reset Content',
    206: b'Partial Content',
    207: b'Multi-Status',
    208: b'Already Reported',
    226: b'IM Used',
    300: b'Multiple Choices',
    301: b'Moved Permanently',
    302: b'Found',
    303: b'See Other',
    304: b'Not Modified',
    305: b'Use Proxy',
    307: b'Temporary Redirect',
    308: b'Permanent Redirect',
    400: b'Bad Request',
    401: b'Unauthorized',
    402: b'Payment Required',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    406: b'Not Acceptable',
    407: b'Proxy Authentication Required',
    408: b'Request Timeout',
    409: b'Conflict',
    410: b'Gone',
    411: b'Length Required',
    412: b'Precondition Failed',
    413: b'Request Entity Too Large',
    414: b'Request-URI Too Long',
    415: b'Unsupported Media Type',
    416: b'Requested Range Not Satisfiable',
    417: b'Expectation Failed',
    418: b'I\'m a teapot',
    422: b'Unprocessable Entity',
    423: b'Locked',
    424: b'Failed Dependency',
    426: b'Upgrade Required',
    428: b'Precondition Required',
    429: b'Too Many Requests',
    431: b'Request Header Fields Too Large',
    451: b'Unavailable For Legal Reasons',
    500: b'Internal Server Error',
    501: b'Not Implemented',
    502: b'Bad Gateway',
    503: b'Service Unavailable',
    504: b'Gateway Timeout',
    505: b'HTTP Version Not Supported',
    506: b'Variant Also Negotiates',
    507: b'Insufficient Storage',
    508: b'Loop Detected',
    510: b'Not Extended',
    511: b'Network Authentication Required',
}

DEFAULT_TYPE = cast(
    Dict[int, str],
    {
        1: "application/octet-stream",
        2: "text/plain",
        3: "application/json",
        4: "text/html",
    },
)


class Response(object):
    """
    响应类
    """
    __slots__ = [
        "_loop",
        "_transport",
        "_version",
        "_socket",
        "_fileno",
        "_headers",
        "_status",
        "_message",
        "length",
        "_body",
        "_charset",
        "_cookies",
        "_headers_sent",
        "type",
        "_app",
        "_default_charset",
        "request",
        "ctx",
    ]

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            transport: asyncio.Transport,
            version: str = DEFAULT_HTTP_VERSION,
            charset: str = DEFAULT_RESPONSE_CODING,
    ) -> None:
        self._loop = loop
        self._transport = transport
        self._version = version
        self._socket = cast(
            socket,
            transport.get_extra_info("socket"),
        )
        self._fileno = self._socket.fileno()
        self._headers = cast(HEADER_TYPE, {})
        self._status = 200
        self._message = b"OK"
        self.length = cast(Optional[int], None)
        self.type = cast(Optional[str], None)
        self._body = cast(
            Union[
                bytes,
                str,
                List[Any],
                Dict[Any, Any],
                RawIOBase,
                None,
            ],
            None,
        )
        # self._body_type: int = BodyType.undefined
        self._charset = cast(Optional[str], None)
        self._default_charset = charset
        self._headers_sent = False
        self._cookies = Cookies()
        self._app = cast(Any, None)
        self.request = cast(Any, None)
        self.ctx = cast(Any, None)

    @property
    def app(self) -> Any:
        """
        应用实例
        """
        return self._app

    @app.setter
    def app(self, app: Any) -> None:
        """
        设置应用实例
        """
        self._app = app

    @property
    def headers_sent(self) -> bool:
        """
        headers 是否发送
        """
        return self._headers_sent

    # @headers_sent.setter
    # def headers_sent(self, sent: bool) -> None:
    #     self._headers_sent = sent

    @property
    def status(self) -> int:
        """
        获取响应状态
        """
        return self._status

    @status.setter
    def status(self, status: int) -> None:
        """
        设置响应状态
        """
        self._status = status
        self._message = STATUS_CODES[status]

    def sync_write(self, data: bytes) -> None:
        """
        同步写入socket
        """
        os.write(self._fileno, data)

    def write(self, data: bytes, sync: bool = False) -> None:
        """
        异步写入，通过 asyncio 的原生异步
        """
        if sync:
            self.sync_write(data)
        else:
            self._transport.write(data)

    def get(self, name: str) -> Union[None, str, List[str]]:
        """
        获取 header
        """
        if name in self._headers:
            return self._headers[name]
        return None

    def set(self, name: str, value: Union[str, List[str]]) -> None:
        """
        设置 header
        """
        self._headers[name] = value

    @property
    def header(self) -> HEADER_TYPE:
        """
        获取 headers
        """
        return self._headers

    @property
    def headers(self) -> HEADER_TYPE:
        """
        获取 headers
        """
        return self._headers

    @property
    def body(self) -> Union[bytes, str, List[Any], Dict[Any, Any], RawIOBase, None]:
        """
        获取body
        """
        return self._body

    @body.setter
    def body(self, body: Union[bytes, str, list, dict, RawIOBase, None]) -> None:
        """
        设置body
        """
        self._body = body

    def handel_default(self) -> None:
        """
        处理设置到body上的数据默认 headers
        """
        raw_body = self._body
        body = cast(Optional[bytes], None)
        default_type = 2
        charset = self._charset or self._default_charset
        if raw_body is None:
            pass
        elif isinstance(raw_body, bytes):
            # body为bytes
            default_type = 2
            body = raw_body
        elif isinstance(raw_body, str):
            # body 为字符串
            default_type = 2
            body = encode_str(raw_body, charset)
        elif isinstance(raw_body, (list, dict)):
            # body 为json
            default_type = 3
            body = encode_str(json.dumps(raw_body, ensure_ascii=False), charset)
        elif isinstance(raw_body, RawIOBase):
            # body 为文件
            default_type = 1
            body = raw_body.read()
            raw_body.close()
        if "Content-Length" not in self._headers and \
                "Transfer-Encoding" not in self._headers \
                or self._headers["Transfer-Encoding"] != "chunked":
            if self.length is None:
                if body is not None:
                    self.length = len(body)
                else:
                    self.length = 0
            # 设置默认 Content-Length
            self.set("Content-Length", str(self.length))
        # print(body[0], body[1])
        if body is not None and body.startswith(encode_str("<", charset)):
            default_type = 4
        if "Content-Type" not in self._headers.keys():
            type_str = self.type
            if type_str is None:
                temp = DEFAULT_TYPE.get(default_type)
                if temp is not None:
                    if default_type != 1:
                        temp += "; charset=%s" % charset
                    type_str = temp
            if type_str is not None:
                # 设置默认 Content-Type
                self.set("Content-Type", type_str)
        self._body = body

    def flush_headers(self, sync: bool = False) -> None:
        """
        通过异步写入 header
        """
        if self._headers_sent:
            return
        self._headers_sent = True
        self.handel_default()
        self.write(
            b"HTTP/%s %d %s\r\n" % (
                encode_str(self._version),
                self._status,
                self._message,
            ),
            sync,
        )
        for name, value in self._headers.items():
            name_byte = encode_str(name)
            if isinstance(value, list):
                for val in value:
                    self.write(
                        b"%s: %s\r\n" % (
                            name_byte,
                            encode_str(val),
                        ),
                        sync,
                    )
            else:
                val = value
                self.write(
                    b"%s: %s\r\n" % (
                        name_byte,
                        encode_str(value),
                    ),
                    sync,
                )
        self.write(b"\r\n", sync)

    def flush_body(self) -> bool:
        """
        发送内容体
        """
        if self._body is None:
            return False
        elif isinstance(self._body, bytes):
            self.write(self._body)
            return True
        return False

    @property
    def cookies(self) -> Cookies:
        """
        获取cookies
        """
        return self._cookies
