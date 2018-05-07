import asyncio
from typing import Any
from urllib.parse import urlencode
# from aiko import App

from aiko import Request
from .utils import BaseTest, run_until_complete


class TestRequest(BaseTest):

    @run_until_complete
    @asyncio.coroutine
    def test_request_attrib(self) -> Any:
        @asyncio.coroutine
        def request_complete() -> None:
            pass
        self.request = Request(self.loop, request_complete)
        # self.parser = HttpRequestParser(self.request)
        assert self.request.url == ""
        assert self.request.original_url == ""
        assert self.request.length is None
        self.request.on_url(b"/?" + urlencode({"test": "测试"}).encode())
        self.request.on_header(b"Host", b"127.0.0.1:8006")
        self.request.on_header(b"Content-Length", b"5")
        assert self.request.url == r"/?test=%E6%B5%8B%E8%AF%95"
        assert self.request.original_url == r"/?test=%E6%B5%8B%E8%AF%95"
        assert self.request.length == 5
        assert self.request.get("Host") == "127.0.0.1:8006"
        assert self.request.querystring == r"test=%E6%B5%8B%E8%AF%95"
        assert self.request.query["test"][0] == "测试"
        assert self.request.querystring == self.request.search
        assert self.request.schema == "http"
        assert not self.request.secure
        assert self.request.charset is None
        assert self.request.type is None
        assert self.request.host == "127.0.0.1:8006"
        assert self.request.hostname == "127.0.0.1"
        assert self.request.ips == []
        self.request.on_header(b"Content-Type", b"text/plan; charset=utf-8")
        assert self.request.charset == "utf-8"
        assert self.request.type == 'text/plan'
