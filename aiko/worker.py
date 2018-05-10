# -*- coding: utf-8 -*-
"""
提供给gunicorn 进行多进程的 Worker
"""

import asyncio
import os
from asyncio.base_events import Server as AIOServer
from ssl import SSLContext
from typing import Any, cast, Dict, Generator, List, Optional, Tuple

from gunicorn.workers.base import Worker


class GunicornWorker(Worker):
    """
    基本 Worker 把 gunicorn 分配的 sock 创建为 Server
    """
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.loop = cast(Optional[asyncio.AbstractEventLoop], None)
        self.servers = cast(List[AIOServer], [])
        self.alive = True

    def init_process(self) -> None:
        """
        GunicornWorker 初始化回调
        """
        default_loop = asyncio.get_event_loop()
        if default_loop.is_running():
            default_loop.close()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        else:
            self.loop = default_loop
        super().init_process()

    def run(self) -> None:
        """
        创建了 sock 的运行回调
        """
        if self.loop is None:
            return
        create_server = asyncio.ensure_future(self._run(), loop=self.loop)  # type: ignore
        try:
            self.loop.run_until_complete(create_server)
            self.loop.run_until_complete(self._check_alive())
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    @asyncio.coroutine
    def _check_alive(self) -> Generator[Any, None, None]:
        """
        等待结束信号
        """
        if self.loop is None:
            return
        pid = os.getpid()
        try:
            while self.alive:  # type: ignore
                self.notify()

                if pid == os.getpid() and self.ppid != os.getppid():
                    self.alive = False
                    self.log.info("Parent changed, shutting down: %s", self)
                else:
                    yield from asyncio.sleep(1.0, loop=self.loop)
        except (Exception, BaseException, GeneratorExit, KeyboardInterrupt):
            pass
        yield from self.close()

    @asyncio.coroutine
    def _run(self) -> Generator[Any, None, None]:
        """
        创建 Server
        """
        ssl_context = self._create_ssl_context()
        # access_logger = self.log.access_log if self.cfg.accesslog else None
        for sock in self.sockets:
            # max_fields_size = self.cfg.limit_request_fields * self.cfg.limit_request_field_size
            # h11_max_incomplete_size = self.cfg.limit_request_line + max_fields_size
            server = yield from self.wsgi.create_server(self.loop, sock=sock.sock, ssl=ssl_context)
            self.servers.append(server)

    def _create_ssl_context(self) -> Optional[SSLContext]:
        """
        创建 ssl
        """
        ssl_context = None
        if self.cfg.is_ssl:
            ssl_context = SSLContext(self.cfg.ssl_version)
            ssl_context.load_cert_chain(self.cfg.certfile, self.cfg.keyfile)
            if self.cfg.ca_certs:
                ssl_context.load_verify_locations(self.cfg.ca_certs)
            if self.cfg.ciphers:
                ssl_context.set_ciphers(self.cfg.ciphers)
            ssl_context.set_alpn_protocols(['http/1.1'])
        return ssl_context

    @asyncio.coroutine
    def close(self) -> Generator[Any, None, None]:
        """
        关闭回调
        """
        for server in self.servers:
            server.close()
            yield from server.wait_closed()


class GunicornUVLoopWorker(GunicornWorker):
    """
    使用uvloop的 Worker
    """
    def init_process(self) -> None:
        """
        关闭上次的loop，使用新的loop.
        """
        import uvloop
        asyncio.get_event_loop().close()
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        super().init_process()
