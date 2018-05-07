import asyncio
import unittest
from asyncio.base_events import Server
from functools import wraps
from typing import Any, cast, Optional

from aiko import App


def run_until_complete(fun: Any) -> Any:
    if not asyncio.iscoroutinefunction(fun):
        fun = asyncio.coroutine(fun)

    @wraps(fun)
    def wrapper(test: 'BaseTest', *args: Any, **kw: Any) -> Any:
        loop = test.loop
        temp = asyncio.wait_for(
            fun(
                test,
                *args,
                **kw,
            ),
            15,
            loop=loop,
        )
        ret = loop.run_until_complete(temp)
        return ret
    return wrapper


class BaseTest(unittest.TestCase):
    """Base test case for unittests.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.loop = cast(asyncio.AbstractEventLoop, None)

    def setUp(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self) -> None:
        self.loop.close()
        self.loop = cast(asyncio.AbstractEventLoop, None)


class AppTest(BaseTest):
    HOST = "0.0.0.0"
    PORT = 8006

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.server: Optional[Server] = None
        self.app: Optional[App] = None

    def setUp(self) -> None:
        super().setUp()
        self.app = App(self.loop)

    @asyncio.coroutine
    def listen(self) -> Any:
        if self.server is None:
            self.server = yield from self.app.listen(
                host=self.HOST,
                port=self.PORT,
            )

    @asyncio.coroutine
    def unlisten(self) -> Any:
        if self.server is not None:
            self.server.close()
            yield from self.server.wait_closed()
            self.server = None

    def tearDown(self) -> None:
        if self.server is not None:
            self.server.close()
            self.server = None
        super().tearDown()
