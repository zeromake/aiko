import asyncio
from aiko import App
from .utils import BaseTest, run_until_complete
import aiohttp

class TestRequest(BaseTest):

    @run_until_complete
    def test_url(self):
        yield from self.listen()
        url = "http://127.0.0.1:%d/test" % self.PORT
        temp = ""

        def midd(ctx, next_call):
            nonlocal temp
            temp = ctx.request.url
            return "1"
        self.app.use(midd)
        session = aiohttp.ClientSession()
        r = yield from session.get(url)
        assert r.status == 200
        assert (yield from r.text()) == "1"
        assert temp == "/test"
