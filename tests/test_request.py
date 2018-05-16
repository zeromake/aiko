import asyncio
from typing import Any, cast
from urllib.parse import urlencode
# from aiko import App

from httptools import HttpRequestParser

from aiko import Request
from .utils import BaseTest, run_until_complete


class TestRequest(BaseTest):

    @run_until_complete
    @asyncio.coroutine
    def test_request_attrib(self) -> Any:
        future = self.loop.create_future()
        host = "127.0.0.1:8006"
        query = {"test": "测试"}
        query_string = urlencode(query)
        url = "/?" + query_string

        def request_complete() -> None:
            try:
                # url host
                assert self.request.url == url
                assert self.request.original_url == url
                assert self.request.get("Host") == host
                assert self.request.querystring == query_string
                assert cast(Any, self.request.query)["test"][0] == query["test"]
                assert self.request.querystring == self.request.search
                assert self.request.host == host
                assert self.request.hostname == host.split(":")[0]
                assert self.request.path == "/"
                assert self.request.length is None
                assert self.request.schema == "http"
                # socket or other
                assert not self.request.secure
                assert self.request.ips is None
                assert self.request.charset == "utf-8"
                assert self.request.type == 'text/plan'
                assert self.request.socket is None
                future.set_result(True)
            except AssertionError as e:
                future.set_exception(e)

        self.request = Request(self.loop)
        self.request.once("request", request_complete)
        self.parser = HttpRequestParser(self.request)
        self.request.parser = self.parser
        self.request.feed_data(
            b"\r\n".join([
                b"GET %s HTTP/1.1" % url.encode(),
                b"Host: %s" % host.encode(),
                b"Connection: keep-alive",
                b"Content-Type: text/plan; charset=utf-8",
                b"",
                b"",
            ]),
        )
        yield from future
        self.request = cast(Any, None)
        self.parser = cast(Any, None)
