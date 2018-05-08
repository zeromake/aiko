aiko
======

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

Links
-----

.. _koa: https://github.com/koajs/koa

Todo
----

- [ ] request api like koa
    - [ ] `url`
    - [ ] `path`
    - [ ] `query`
    - [ ] `querystring`
    - [ ] `search`
    - [ ] `originalUrl` -> `original_url`
    - [ ] `href`
    - [x] `origin`
    - [x] `protocol`
    - [x] `host`
    - [x] `hostname`
    - [x] `ips`
    - [x] `ip`
    - [x] `proxy`
    - [x] `secure`
    - [x] `charset`
    - [x] `type`
    - [x] `header`
    - [x] `headers`
    - [x] `socket`
    - [x] `set`
    - [x] `get`
- [ ] response api like koa
