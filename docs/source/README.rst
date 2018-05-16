aiko
======

.. image:: https://www.travis-ci.org/zeromake/aiko.svg?branch=master
    :target: https://www.travis-ci.org/zeromake/aiko
    :alt: travis

.. image:: https://ci.appveyor.com/api/projects/status/d0278sgcp77uuqo6?svg=true
    :target: https://ci.appveyor.com/project/zeromake/aiko
    :alt: appveyor

.. image:: https://codecov.io/gh/zeromake/aiko/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/zeromake/aiko
    :alt: codecov

.. image:: https://badge.fury.io/py/aiko.svg
    :target: https://pypi.org/project/aiko/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/aiko.svg
    :target: https://github.com/zeromake/aiko/blob/master/LICENSE
    :alt: PyPI - License

.. image:: https://img.shields.io/pypi/format/aiko.svg
    :target: https://pypi.org/project/aiko/#files
    :alt: PyPI - Format

.. image:: https://img.shields.io/pypi/pyversions/aiko.svg
    :alt: PyPI - PyVersions

aiko is a base asyncio's lightweight web application framework.
It is designed to make `koa`_ api.

Installing
----------

Install by code

.. code-block:: text

    $ git clone https://github.com/zeromake/aiko
    $ cd aiko
    $ python setup.py install

A Simple Example
----------------

.. code-block:: python

    import asyncio
    from aiko import App

    loop = asyncio.get_event_loop()
    app = App(loop)

    def hello(ctx, next_call):
        return "Hello, World!"

    app.use(hello)

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)

.. code-block:: text

    $ curl http://127.0.0.1:5000
    Hello, World!

Todo
----

- [ ] request api like koa
    - [ ] method
        - [ ] `accepts`
        - [ ] `acceptsEncodings` -> `accepts_encodings`
        - [ ] `acceptsCharsets` -> `accepts_charsets`
        - [ ] `acceptsLanguages` -> `accepts_languages`
        - [ ] `is`
        - [x] `get`
    - [ ] getter, setter
        - [x] `header`
            - [x] getter
            - [ ] setter
        - [x] `headers`
            - [x] getter
            - [ ] setter
        - [x] `url`
        - [x] `origin`
        - [x] `href`
        - [x] `method`
        - [x] `path`
        - [x] `query`
        - [x] `querystring`
        - [x] `search`
    - [ ] getter
        - [x] `host`
        - [x] `hostname`
        - [ ] `URL`
        - [x] `fresh`
        - [x] `stale`
        - [x] `idempotent`
        - [x] `socket`
        - [x] `charset`
        - [x] `length`
        - [x] `protocol`
        - [x] `secure`
        - [x] `ips`
        - [ ] `subdomains`
        - [x] `type`
        - [x] `originalUrl` -> `original_url`
        - [x] `ip`
- [ ] response api like koa
- [x] proxy class property attr and method
- [x] like `fresh`_ method
- [ ] request.`on_body` pause_reading designed by `uvicorn`_

Reference by
------------

+ http framework
    - `koa`_ node 上的简洁 api 的 http framework
    - `sanic`_ 使用 asyncio + httptools，api 类似 flask 源代码混乱。
    - `quart`_ 使用 asyncio，api 兼容 flask 解析器过慢。
    - `uvicorn`_ 使用 asyncio + httptools, asgi 规范实现。
    - `japronto`_ 使用 asyncio + picohttpparser, 全 c 构建，性能最强。
+ http tools
    - `fresh`_ 判断 `headers` 是否返回 304
+ specification
    - `asgiref`_ asgi 协议
    - `mdn`_ mdn 的 http 协议说明

Links
-----

.. _koa: https://github.com/koajs/koa
.. _uvicorn: https://github.com/encode/uvicorn
.. _sanic: https://github.com/channelcat/sanic
.. _asgiref: https://github.com/django/asgiref
.. _japronto: https://github.com/squeaky-pl/japronto
.. _quart: https://gitlab.com/pgjones/quart
.. _fresh: https://github.com/jshttp/fresh
.. _mdn: https://developer.mozilla.org/zh-CN/docs/Web/HTTP
