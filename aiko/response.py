# -*- coding: utf-8 -*-

import asyncio
import json
import os
from enum import Enum
from io import RawIOBase
from typing import Dict, Optional, Union

from .utils import encode_str

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


class BodyType(Enum):
    undefined = 0
    string = 1
    json = 2
    byte = 3
    stream = 4


class Response(object):
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
        "_default_type",
        "_charset",
        "header_send",
        "body_send",
    ]

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        transport: Optional[asyncio.Transport],
        version: str = "1.1",
    ) -> None:
        self._loop = loop
        self._transport = transport
        self._version = version
        self._socket = transport.get_extra_info("socket")
        self._fileno = self._socket.fileno()
        self._headers: Dict[str, str] = {}
        self._status = 200
        self._message = b"OK"
        self.length: Optional[int] = None
        self._body: Optional[bytes] = None
        # self._body_type: int = BodyType.undefined
        self._charset: Optional[str] = None
        self.header_send: bool = False
        self.body_send: bool = False
        self._default_type: Optional[str] = None

    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, status: int) -> None:
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

    def set(self, name: str, value: str) -> None:
        """
        设置 header
        """
        self._headers[name] = value

    @property
    def header(self) -> Dict[str, str]:
        return self._headers

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def body(self) -> Union[bytes, None]:
        return self._body

    @body.setter
    def body(self, body: Union[bytes, str, list, dict, RawIOBase]) -> None:
        raw_body: Optional[bytes] = None
        if body is None:
            self._default_type = None
        elif isinstance(body, bytes):
            self._default_type = "application/octet-stream"
        elif isinstance(body, str):
            self._default_type = "text/plain"
            raw_body = encode_str(body)
        elif isinstance(body, (list, dict)):
            self._default_type = "application/json"
            raw_body = encode_str(json.dumps(body))
        elif isinstance(body, RawIOBase):
            self._default_type = "application/octet-stream"
            temp = body.read()
            body.close()
            raw_body = temp
        else:
            self._default_type = None
        self._body = raw_body

    def flush_headers(self, sync: bool = False) -> None:
        """
        通过异步写入 header
        """
        if self.header_send:
            return
        # if self.length is not None and "Content-Length":
        #     self.set("Content-Length", str(self.length))
        self.default_content()
        self.header_send = True
        # headers = BytesIO()
        self.write(
            b"HTTP/%s %d %s\r\n" % (
                encode_str(self._version),
                self._status,
                self._message,
            ),
            sync,
        )
        for name, value in self._headers.items():
            self.write(
                b"%s: %s\r\n" % (
                    encode_str(name),
                    encode_str(value),
                ),
                sync,
            )
        self.write(b"\r\n", sync)
        # headers_byte: bytes = headers.getvalue()
        # self.write(headers_byte, sync)

    def default_content(self) -> None:
        """

        """
        if "Content-Type" not in self.headers and self._default_type:
            self.set("Content-Type", self._default_type)
        if "Content-Length" not in self.headers:
            if self._body is None:
                self.set("Content-Length", "0")
            else:
                length = self.length
                if length is None:
                    length = len(self._body)
                self.set("Content-Length", str(length))

    def flush_body(self) -> None:
        """
        发送内容体
        """
        if self.body_send:
            return
        self.body_send = True
        if self._body is None:
            return
        else:
            self.write(self._body)
