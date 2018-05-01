import asyncio
# from datetime import datetime
from asyncio.base_events import Server
from collections import Generator
from ssl import SSLContext
from types import FunctionType
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Optional,
    Type,
)

from . import (
    Context,
    Request,
    Response,
    ServerProtocol,
)

__all__ = [
    "Application",
    "App",
]


class Application(object):
    __slots__ = [
        "_loop",
        "_protocol",
        "_request",
        "_response",
        "_context",
        "_middleware",
    ]

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        protocol: Type[ServerProtocol] = ServerProtocol,
        request: Type[Request] = Request,
        response: Type[Response] = Response,
        context: Type[Context] = Context,
    ) -> None:
        self._loop = loop
        self._protocol = protocol
        self._request = request
        self._response = response
        self._context = context
        self._middleware: List[FunctionType] = []

    @asyncio.coroutine
    def listen(self, **kwargs: Any) -> Server:
        return (yield from self._loop.create_server(
            lambda: self._protocol(
                loop=self._loop,
                handle=self._handle,
            ),
            **kwargs,
        ))

    def run(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        listen = self.listen(host=host, port=port)
        self._loop.run_until_complete(listen)
        self._loop.run_forever()

    @asyncio.coroutine
    def create_server(
        self,
        loop: asyncio.AbstractEventLoop,
        sock: Any,
        ssl: SSLContext,
    ) -> Server:
        if loop is not None and self._loop is not loop:
            self._loop = loop
        return (yield from self.listen(
            sock=sock,
            ssl=ssl,
        ))

    def _next_middleware(self, middlewares: Iterator[FunctionType], ctx: Context) -> Callable[[], Any]:
        @asyncio.coroutine
        def next_call() -> Any:
            yield from self._middleware_call(middlewares, ctx)
        return next_call

    @asyncio.coroutine
    def _middleware_call(self, middlewares: Iterator[FunctionType], ctx: Context) -> Any:
        middleware = None
        try:
            middleware = next(middlewares)
        except StopIteration:
            return
        next_call = self._next_middleware(middlewares, ctx)
        if asyncio.iscoroutinefunction(middleware):
            body = yield from middleware(ctx, next_call)
        else:
            body = middleware(ctx, next_call)
        if body is not None:
            if isinstance(body, Generator):
                for gen in body:
                    if gen is None:
                        continue
                    if asyncio.iscoroutine(gen):
                        try:
                            gen = yield from gen
                        except Exception as e:
                            body.send(e)
                            continue
                    if gen is not None:
                        body = gen
                if isinstance(body, Generator):
                    body = None
            elif asyncio.iscoroutine(body):
                try:
                    body = yield from body
                except Exception:
                    pass
            if body is not None:
                ctx.response.body = body

    @asyncio.coroutine
    def _handle(self, request: Request, response: Response) -> Any:
        # request.start_time = datetime.now().timestamp()
        ctx = self._context(self._loop, request, response)
        yield from self._middleware_call(iter(self._middleware), ctx)
        ctx.response.flush_headers()
        ctx.response.flush_body()

    def use(self, middleware: FunctionType) -> None:
        self._middleware.append(middleware)

    def __call__(self) -> 'Application':
        return self


App = Application
