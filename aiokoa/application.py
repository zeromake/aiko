# -*- coding: utf-8 -*-

import asyncio
# from datetime import datetime
from asyncio.base_events import Server
from collections import Generator
from signal import (
    SIGINT,
    SIGTERM,
)
from ssl import SSLContext
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Generator as TypeGenerator,
    Iterator,
    List,
    Optional,
    Type,
    Union,
)

from .context import Context
from .request import Request
from .response import Response
from .server import ServerProtocol

__all__ = [
    "Application",
    "App",
]

next_call_res_type = TypeGenerator[Any, None, None]
next_call_type = Callable[[], next_call_res_type]
middleware_res_type = Union[
    bytes,
    str,
    None,
]
middleware_type = Callable[
    [Context, next_call_type],
    Union[
        middleware_res_type,
        TypeGenerator[Any, None, middleware_res_type],
        AsyncIterable[middleware_res_type],
    ],
]


class Application(object):
    """Application
    Usually you create a :class:`Application` instance in your main module or
    in the :file:`__init__.py` file of your package like this::
        import asyncio
        from aiokoa import App

        loop = asyncio.get_event_loop()
        app = App(loop)
    :param loop: asyncio.AbstractEventLoop
    :param protocol: ServerProtocol class
    :param request: Request class
    :param response: Response class
    :param context: Context class
    """

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
        self._middleware: List[middleware_type] = []

    @property
    def context(self) -> Type[Context]:
        """
        获得 context class
        """
        return self._context

    @property
    def request(self) -> Type[Request]:
        """
        获得 request class
        """
        return self._request

    @property
    def response(self) -> Type[Response]:
        """
        获得 response class
        """
        return self._response

    @asyncio.coroutine
    def listen(self, **kwargs: Any) -> Server:
        """
        bind host, port or sock
        """
        return (yield from self._loop.create_server(
            lambda: self._protocol(
                loop=self._loop,
                handle=self._handle,
            ),
            **kwargs,
        ))

    def run(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        """
        debug run
        :param host: the hostname to listen on, default is ``'0.0.0.0'``
        :param port: the port of the server, default id ``5000``
        """
        listen = self.listen(host=host, port=port)
        server = self._loop.run_until_complete(listen)

        def close() -> None:
            server.close()
            self._loop.stop()
        # print(type(server))
        self._loop.add_signal_handler(SIGTERM, close)
        self._loop.add_signal_handler(SIGINT, close)
        self._loop.run_forever()

    @asyncio.coroutine
    def create_server(
        self,
        loop: asyncio.AbstractEventLoop,
        sock: Any,
        ssl: SSLContext,
    ) -> TypeGenerator[Any, None, Server]:
        if loop is not None and self._loop is not loop:
            self._loop = loop
        return (yield from self.listen(
            sock=sock,
            ssl=ssl,
        ))

    def _next_middleware(
        self,
        middlewares: Iterator[middleware_type],
        ctx: Context,
    ) -> next_call_type:
        """
        生成 next_call 的调用
        使用迭代器，这个方法每调用一次都会指向下一个中间件。
        """
        @asyncio.coroutine
        def next_call() -> next_call_res_type:
            yield from self._middleware_call(middlewares, ctx, next_call)
        return next_call

    @asyncio.coroutine
    def _middleware_call(
        self,
        middlewares: Iterator[middleware_type],
        ctx: Context,
        next_call: next_call_type,
    ) -> Any:
        """
        从迭代器中取出一个中间件，执行
        """
        middleware = None
        try:
            middleware = next(middlewares)
        except StopIteration:
            return
        # next_call = self._next_middleware(middlewares, ctx)
        if asyncio.iscoroutinefunction(middleware):
            temp: Any = middleware(ctx, next_call)
            body = yield from temp
        else:
            body = middleware(ctx, next_call)
        if body is not None:
            if isinstance(body, Generator):
                # 处理同步方法使用 yield 来调用异步
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
                # 处理中间件返回了一个 coroutine 对象需要 await
                try:
                    body = yield from body
                except Exception:
                    pass
            # 中间件返回的结果如果不为空设置到 body
            if body is not None:
                ctx.response.body = body

    @asyncio.coroutine
    def _handle(self, request: Request, response: Response) -> Any:
        """
        request 解析后的回调，调用中间件，并处理 headers, body 发送。
        """
        # request.start_time = datetime.now().timestamp()
        # 创建一个新的会话上下文
        ctx = self._context(self._loop, request, response)
        # 把当前注册的中间件转为迭代器
        middleware_iter = iter(self._middleware)
        # 通过迭代器的模式生成一个执行下一个中间的调用方法
        next_call = self._next_middleware(middleware_iter, ctx)
        # 顺序执行中间件
        yield from self._middleware_call(middleware_iter, ctx, next_call)
        # 写出 headers
        ctx.response.flush_headers()
        # 写出 body
        ctx.response.flush_body()

    def use(self, middleware: middleware_type) -> None:
        """
        插入一个中间件
        """
        self._middleware.append(middleware)

    def __call__(self) -> 'Application':
        """
        用于 Gunicorn 的 wsgi 模式
        """
        return self


# Application 别名
App = Application
