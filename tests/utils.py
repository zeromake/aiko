import asyncio
import unittest
from aiko import App
from functools import wraps
from typing import Optional, cast


def run_until_complete(fun):
    if not asyncio.iscoroutinefunction(fun):
        fun = asyncio.coroutine(fun)

    @wraps(fun)
    def wrapper(test, *args, **kw):
        loop = test.loop
        ret = loop.run_until_complete(
            asyncio.wait_for(fun(test, *args, **kw), 15, loop=loop))
        return ret
    return wrapper

class BaseTest(unittest.TestCase):
    """Base test case for unittests.
    """
    HOST = "0.0.0.0"
    PORT = 8006

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = cast(asyncio.AbstractEventLoop, None)
        self.server: Optional[asyncio.Server] = None

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.app = App(self.loop)
    
    @asyncio.coroutine
    def listen(self):
        if self.server is None:
            self.server = yield from self.app.listen(
                host=self.HOST,
                port=self.PORT,
            )

    @asyncio.coroutine
    def unlisten(self):
        if self.server is not None:
            self.server.close()
            yield from self.server.wait_closed()
            self.server = None

    def tearDown(self):
        if self.server is not None:
            self.server.close()
            self.server = None
        self.loop.close()
        self.loop = cast(asyncio.AbstractEventLoop, None)
